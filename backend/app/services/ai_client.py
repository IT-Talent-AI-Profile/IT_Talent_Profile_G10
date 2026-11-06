import json
import requests

from pydantic import ValidationError

from app.core.config import settings
from app.schemas.cv import CvResult
from app.services.prompts import build_cv_extraction_prompt, build_summary_prompt


ANTHROPIC_API_URL = "https://api.anthropic.com/v1/messages"
ANTHROPIC_MODEL = "claude-sonnet-5"
ANTHROPIC_VERSION = "2023-06-01"

MAX_RETRIES = 2
TIMEOUT = 30
MAX_CV_CHARS = 12000


def call_ai(prompt: str) -> str:
    api_key = settings.AI_API_KEY

    if not api_key:
        raise RuntimeError("Chưa cấu hình AI_API_KEY")

    headers = {
        "x-api-key": api_key,
        "anthropic-version": ANTHROPIC_VERSION,
        "content-type": "application/json"
    }

    payload = {
        "model": ANTHROPIC_MODEL,
        "max_tokens": 4096,
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ]
    }

    try:
        response = requests.post(
            ANTHROPIC_API_URL,
            headers=headers,
            json=payload,
            timeout=TIMEOUT
        )

        response.raise_for_status()

        data = response.json()
        content = data.get("content", [])

        text_blocks = [
            block.get("text", "")
            for block in content
            if block.get("type") == "text"
        ]

        if not text_blocks:
            raise RuntimeError(
                "Claude API không trả về nội dung văn bản"
            )

        return "\n".join(text_blocks).strip()

    except requests.Timeout as error:
        raise RuntimeError(
            "Claude API đã vượt quá thời gian chờ 30 giây"
        ) from error

    except requests.HTTPError as error:
        response = error.response
        status_code = response.status_code if response is not None else "Unknown"

        try:
            message = response.json().get("error", {}).get(
                "message", response.text
            )
        except (ValueError, AttributeError):
            message = response.text if response is not None else str(error)

        raise RuntimeError(
            f"Claude API trả về lỗi HTTP {status_code}: {message}"
        ) from error

    except requests.RequestException as error:
        raise RuntimeError(
            f"Không thể kết nối Claude API: {error}"
        ) from error


def _parse_ai_response(response_text: str) -> CvResult:
    cleaned_text = response_text.strip()

    if cleaned_text.startswith("```"):
        cleaned_text = cleaned_text.split("\n", 1)[-1]

        if cleaned_text.endswith("```"):
            cleaned_text = cleaned_text[:-3]

        cleaned_text = cleaned_text.strip()

    result_data = json.loads(cleaned_text)

    return CvResult.model_validate(result_data)


def _mock_extract_cv(skill_catalog: list[str]) -> CvResult:
    mock_skills = []

    if skill_catalog:
        mock_skills.append({
            "name": skill_catalog[0],
            "proficiency": 3,
            "years": 1.0
        })

    return CvResult(
        skills=mock_skills,
        years_experience=1.0,
        education="Đại học Công nghệ Thông tin",
        experience="Có 1 năm kinh nghiệm phát triển phần mềm"
    )


def extract_cv(
    cv_text: str,
    skill_catalog: list[str] | None = None
) -> CvResult:

    if not cv_text or not cv_text.strip():
        raise ValueError("Nội dung CV không được để trống")

    cv_text = cv_text[:MAX_CV_CHARS]
    skill_catalog = skill_catalog or []

    if (
        settings.AI_MODE.lower() == "mock"
        or not settings.AI_API_KEY
    ):
        return _mock_extract_cv(skill_catalog)

    prompt = build_cv_extraction_prompt(
        cv_text=cv_text,
        skill_catalog=skill_catalog
    )

    last_error = None

    for attempt in range(MAX_RETRIES + 1):
        try:
            response_text = call_ai(prompt)
            result = _parse_ai_response(response_text)

            allowed_skills = {
                skill.lower() for skill in skill_catalog
            }

            result.skills = [
                skill for skill in result.skills
                if skill.name.lower() in allowed_skills
            ]

            return result

        except (json.JSONDecodeError, ValidationError, ValueError) as error:
            last_error = error

            if attempt < MAX_RETRIES:
                prompt += """

Phản hồi trước đó không đúng định dạng JSON
hoặc không đáp ứng cấu trúc dữ liệu yêu cầu.

Hãy tạo lại JSON hợp lệ theo đúng cấu trúc.
Chỉ trả về JSON, không thêm nội dung khác.
"""

    raise ValueError(
        f"Không thể phân tích phản hồi AI sau 3 lần thử: {last_error}"
    ) from last_error


def _limit_words(text: str, max_words: int = 150) -> str:
    """Giới hạn tối đa số từ của đoạn văn bản."""
    words = text.strip().split()
    if len(words) <= max_words:
        return text.strip()
    return " ".join(words[:max_words]).strip()


def make_summary(
    skills: list | None = None,
    score: float | None = None,
    level: str | None = None
) -> str:
    """
    Tạo bản tóm tắt năng lực (điểm mạnh, điểm yếu) tối đa 150 từ (Task [AI-03]):
    - Gửi danh sách kỹ năng, điểm và cấp độ cho AI.
    - Có chế độ mock khi AI_MODE=mock hoặc không có AI_API_KEY.
    - Nếu AI lỗi (mất mạng, timeout, lỗi API) thì trả chuỗi rỗng (không để làm hỏng cả luồng).
    """
    # 1. Chế độ Mock
    if (
        settings.AI_MODE.lower() == "mock"
        or not settings.AI_API_KEY
    ):
        skills_sample = []
        if skills:
            for s in skills:
                if isinstance(s, dict):
                    skills_sample.append(s.get("name", ""))
                elif isinstance(s, str):
                    skills_sample.append(s)
                elif hasattr(s, "name"):
                    skills_sample.append(s.name)

        skills_str = ", ".join(skills_sample[:3]) if skills_sample else "lập trình cơ bản"
        lvl = level or "Junior"
        scr = f"{score:.1f}" if score is not None else "65.0"

        mock_text = (
            f"Ứng viên đạt cấp độ {lvl} với điểm đánh giá {scr}/100. "
            f"Điểm mạnh: Nắm vững các công nghệ {skills_str}, tư duy logic tốt và khả năng học hỏi công nghệ mới nhanh. "
            f"Điểm yếu: Cần trau dồi thêm kinh nghiệm thực chiến với các dự án thực tế quy mô lớn, tối ưu hóa hệ thống "
            f"và nâng cấp kỹ năng làm việc nhóm trong môi trường agile."
        )
        return _limit_words(mock_text, 150)

    # 2. Chế độ gọi AI thật
    try:
        prompt = build_summary_prompt(skills=skills, score=score, level=level)
        response_text = call_ai(prompt)
        cleaned = response_text.strip().strip('"').strip("'")
        if cleaned.startswith("```"):
            cleaned = cleaned.split("\n", 1)[-1]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]
            cleaned = cleaned.strip()
        return _limit_words(cleaned, 150)
    except Exception:
        # Nếu AI lỗi (mất mạng, timeout, API lỗi) thì trả chuỗi rỗng
        return ""
