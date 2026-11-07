import json
import pytest
import requests

from unittest.mock import Mock
from pydantic import ValidationError

from app.schemas.cv import CvResult
from app.services import ai_client


def test_extract_cv_mock(monkeypatch):
    monkeypatch.setattr(ai_client.settings, "AI_MODE", "mock")
    monkeypatch.setattr(ai_client.settings, "AI_API_KEY", "")

    result = ai_client.extract_cv("CV mẫu", ["Python", "Java"])

    assert isinstance(result, CvResult)
    assert len(result.skills) > 0
    assert result.skills[0].name == "Python"


def test_make_summary():
    result = ai_client.make_summary()

    assert isinstance(result, str)
    assert len(result.strip()) > 0
    assert len(result.split()) <= 150


def test_make_summary_with_args_mock(monkeypatch):
    monkeypatch.setattr(ai_client.settings, "AI_MODE", "mock")
    monkeypatch.setattr(ai_client.settings, "AI_API_KEY", "")

    skills = [{"name": "Python", "proficiency": 4, "years": 2.0}]
    result = ai_client.make_summary(skills=skills, score=75.0, level="Middle")

    assert isinstance(result, str)
    assert "Middle" in result
    assert "75.0" in result
    assert len(result.split()) <= 150


def test_make_summary_ai_success(monkeypatch):
    monkeypatch.setattr(ai_client.settings, "AI_MODE", "real")
    monkeypatch.setattr(ai_client.settings, "AI_API_KEY", "test_key")

    mock_text = "Ứng viên có kiến thức tốt về Python và hệ thống backend. Điểm yếu là cần thêm kinh nghiệm thực chiến."
    monkeypatch.setattr(ai_client, "call_ai", lambda prompt: mock_text)

    result = ai_client.make_summary(skills=["Python"], score=80.0, level="Senior")
    assert result == mock_text
    assert len(result.split()) <= 150


def test_make_summary_ai_word_limit(monkeypatch):
    monkeypatch.setattr(ai_client.settings, "AI_MODE", "real")
    monkeypatch.setattr(ai_client.settings, "AI_API_KEY", "test_key")

    long_text = " ".join(["từ"] * 200)
    monkeypatch.setattr(ai_client, "call_ai", lambda prompt: long_text)

    result = ai_client.make_summary(skills=["Python"], score=60.0, level="Junior")
    words = result.split()
    assert len(words) == 150


def test_make_summary_ai_network_error_returns_empty(monkeypatch):
    monkeypatch.setattr(ai_client.settings, "AI_MODE", "real")
    monkeypatch.setattr(ai_client.settings, "AI_API_KEY", "test_key")

    def raise_network_error(prompt):
        raise RuntimeError("Không thể kết nối Claude API: Network is down")

    monkeypatch.setattr(ai_client, "call_ai", raise_network_error)

    # Khi lỗi mạng hoặc AI lỗi, hàm phải trả về chuỗi rỗng và KHÔNG ném ngoại lệ
    result = ai_client.make_summary(skills=["Python"], score=60.0, level="Junior")
    assert result == ""


def test_extract_cv_empty():
    with pytest.raises(ValueError):
        ai_client.extract_cv("", ["Python"])


def test_parse_valid_json():
    response = json.dumps({
        "skills": [
            {
                "name": "Python",
                "proficiency": 3,
                "years": 1
            }
        ],
        "years_experience": 1,
        "education": "Đại học",
        "experience": "Lập trình viên"
    })

    result = ai_client._parse_ai_response(response)

    assert isinstance(result, CvResult)
    assert result.skills[0].name == "Python"
    assert result.years_experience == 1


def test_parse_invalid_json():
    with pytest.raises(json.JSONDecodeError):
        ai_client._parse_ai_response("invalid json")


def test_parse_invalid_schema():
    with pytest.raises(ValidationError):
        ai_client._parse_ai_response(json.dumps({"invalid": "schema"}))


def test_extract_cv_retry(monkeypatch):
    monkeypatch.setattr(ai_client.settings, "AI_MODE", "real")
    monkeypatch.setattr(ai_client.settings, "AI_API_KEY", "test-key")

    calls = []

    def fake_call_ai(prompt):
        calls.append(prompt)

        if len(calls) == 1:
            return "invalid json"

        return json.dumps({
            "skills": [
                {
                    "name": "Python",
                    "proficiency": 3,
                    "years": 1
                }
            ],
            "years_experience": 1,
            "education": None,
            "experience": None
        })

    monkeypatch.setattr(ai_client, "call_ai", fake_call_ai)

    result = ai_client.extract_cv("Nội dung CV", ["Python"])

    assert len(calls) == 2
    assert isinstance(result, CvResult)
    assert result.skills[0].name == "Python"


def test_call_ai_timeout(monkeypatch):
    def timeout_post(*args, **kwargs):
        raise requests.Timeout()

    monkeypatch.setattr(requests, "post", timeout_post)
    monkeypatch.setattr(ai_client.settings, "AI_API_KEY", "test-key")

    with pytest.raises(RuntimeError) as exc_info:
        ai_client.call_ai("test")

    assert "30 giây" in str(exc_info.value)


def test_extract_cv_filters_skills(monkeypatch):
    monkeypatch.setattr(ai_client.settings, "AI_MODE", "real")
    monkeypatch.setattr(ai_client.settings, "AI_API_KEY", "test-key")

    response = json.dumps({
        "skills": [
            {
                "name": "Python",
                "proficiency": 3,
                "years": 1
            },
            {
                "name": "React",
                "proficiency": 2,
                "years": 1
            }
        ],
        "years_experience": 1,
        "education": None,
        "experience": None
    })

    monkeypatch.setattr(
        ai_client,
        "call_ai",
        lambda prompt: response
    )

    result = ai_client.extract_cv("Nội dung CV", ["Python"])

    assert len(result.skills) == 1
    assert result.skills[0].name == "Python"


def test_extract_cv_limits_cv_length(monkeypatch):
    monkeypatch.setattr(ai_client.settings, "AI_MODE", "real")
    monkeypatch.setattr(ai_client.settings, "AI_API_KEY", "test-key")

    captured = {}

    def fake_prompt(cv_text, skill_catalog):
        captured["length"] = len(cv_text)
        return "Prompt test"

    response = json.dumps({
        "skills": [],
        "years_experience": 0,
        "education": None,
        "experience": None
    })

    monkeypatch.setattr(
        ai_client,
        "build_cv_extraction_prompt",
        fake_prompt
    )

    monkeypatch.setattr(
        ai_client,
        "call_ai",
        lambda prompt: response
    )

    ai_client.extract_cv("A" * 15000, ["Python"])

    assert captured["length"] == 12000

def test_call_ai_success(monkeypatch):
    monkeypatch.setattr(ai_client.settings, "AI_API_KEY", "test-key")

    captured = {}

    class FakeResponse:
        def raise_for_status(self):
            pass

        def json(self):
            return {
                "content": [
                    {
                        "type": "text",
                        "text": '{"skills": []}'
                    }
                ]
            }

    def fake_post(url, **kwargs):
        captured["url"] = url
        captured["headers"] = kwargs["headers"]
        captured["payload"] = kwargs["json"]
        captured["timeout"] = kwargs["timeout"]
        return FakeResponse()

    monkeypatch.setattr(ai_client.requests, "post", fake_post)

    result = ai_client.call_ai("Prompt kiểm tra")

    assert result == '{"skills": []}'
    assert captured["url"] == ai_client.ANTHROPIC_API_URL
    assert captured["headers"]["x-api-key"] == "test-key"
    assert captured["headers"]["anthropic-version"] == ai_client.ANTHROPIC_VERSION
    assert captured["payload"]["model"] == ai_client.ANTHROPIC_MODEL
    assert captured["payload"]["messages"][0]["content"] == "Prompt kiểm tra"
    assert captured["timeout"] == 30


def test_build_prompt_contains_cv_and_catalog():
    from app.services.prompts import build_cv_extraction_prompt

    prompt = build_cv_extraction_prompt(
        cv_text="Tôi có 2 năm kinh nghiệm Python",
        skill_catalog=["Python", "Java"]
    )

    assert "Tôi có 2 năm kinh nghiệm Python" in prompt
    assert "Python" in prompt
    assert "Java" in prompt
    assert "JSON hợp lệ" in prompt
    assert "Không tự tạo thêm kỹ năng" in prompt


def test_build_prompt_rejects_empty_cv():
    from app.services.prompts import build_cv_extraction_prompt

    with pytest.raises(ValueError):
        build_cv_extraction_prompt("", ["Python"])
