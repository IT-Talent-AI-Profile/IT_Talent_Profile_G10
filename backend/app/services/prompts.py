MAX_CV_CHARS = 12000


def build_cv_extraction_prompt(
    cv_text: str,
    skill_catalog: list[str]
) -> str:
    """
    Tạo prompt yêu cầu AI phân tích CV và trả về dữ liệu JSON.
    """

    if not cv_text or not cv_text.strip():
        raise ValueError("Nội dung CV không được để trống")

    # Giới hạn nội dung CV tối đa 12.000 ký tự
    cv_text = cv_text[:MAX_CV_CHARS]

    # Chuẩn bị danh mục kỹ năng của hệ thống
    catalog_text = "\n".join(
        f"- {skill}" for skill in skill_catalog
    )

    prompt = f"""
Bạn là chuyên gia tuyển dụng và phân tích hồ sơ ứng viên IT.

Nhiệm vụ của bạn là đọc nội dung CV và trích xuất thông tin
của ứng viên theo các yêu cầu dưới đây.

DANH MỤC KỸ NĂNG ĐƯỢC PHÉP SỬ DỤNG:
{catalog_text}

QUY TẮC PHÂN TÍCH:

1. Chỉ trích xuất kỹ năng xuất hiện trong danh mục kỹ năng
   được cung cấp.
2. Không tự tạo thêm kỹ năng ngoài danh mục.
3. Nếu CV đề cập đến kỹ năng không có trong danh mục,
   hãy bỏ qua kỹ năng đó.
4. proficiency là mức độ thành thạo từ 1 đến 5:
   - 1: Mới bắt đầu
   - 2: Cơ bản
   - 3: Trung bình
   - 4: Thành thạo
   - 5: Chuyên gia
5. years là số năm kinh nghiệm sử dụng kỹ năng đó.
   Nếu không xác định được, sử dụng 0.
6. years_experience là tổng số năm kinh nghiệm làm việc
   của ứng viên, không phải tổng số năm của từng kỹ năng.
7. education là thông tin học vấn.
8. experience là thông tin kinh nghiệm làm việc.
9. Không tự suy đoán thông tin không có trong CV.
10. Nếu không tìm thấy thông tin education hoặc experience,
    hãy trả về null.

ĐỊNH DẠNG KẾT QUẢ:

Chỉ trả về JSON hợp lệ, không sử dụng Markdown,
không thêm lời giải thích hoặc nội dung bên ngoài JSON.

Cấu trúc JSON bắt buộc:

{{
    "skills": [
        {{
            "name": "Python",
            "proficiency": 4,
            "years": 2.5
        }}
    ],
    "years_experience": 2.5,
    "education": "Đại học Công nghệ Thông tin",
    "experience": "Có 2 năm kinh nghiệm phát triển phần mềm"
}}

NỘI DUNG CV CẦN PHÂN TÍCH:

<cv_content>
{cv_text}
</cv_content>
"""

    return prompt.strip()


def build_summary_prompt(
    skills: list | None = None,
    score: float | None = None,
    level: str | None = None
) -> str:
    """
    Tạo prompt yêu cầu AI viết đoạn tóm tắt năng lực (điểm mạnh, điểm yếu), tối đa 150 từ.
    (Phục vụ Task [AI-03])
    """
    skills_repr = []
    if skills:
        for s in skills:
            if isinstance(s, dict):
                name = s.get("name", "")
                prof = s.get("proficiency", "")
                yrs = s.get("years", 0)
                skills_repr.append(f"{name} ({prof}/5, {yrs} năm)")
            elif isinstance(s, str):
                skills_repr.append(s)
            elif hasattr(s, "name"):
                skills_repr.append(s.name)

    skills_text = ", ".join(skills_repr) if skills_repr else "Chưa có kỹ năng ghi nhận"
    score_text = f"{score}/100" if score is not None else "Chưa có điểm"
    level_text = level if level else "Chưa phân cấp"

    prompt = f"""
Bạn là chuyên gia nhân sự và đánh giá năng lực lập trình viên IT.

Dựa vào thông tin hồ sơ dưới đây:
- Cấp độ năng lực: {level_text}
- Điểm đánh giá: {score_text}
- Danh sách kỹ năng: {skills_text}

Nhiệm vụ: Viết một đoạn tóm tắt ngắn gọn bằng tiếng Việt nhận xét về:
1. Điểm mạnh chính của ứng viên.
2. Điểm cần cải thiện / điểm yếu.

YÊU CẦU BẮT BUỘC:
- Độ dài: Tối đa 150 từ.
- Văn phong chuyên nghiệp, khách quan, súc tích.
- Chỉ trả về duy nhất đoạn văn bản tóm tắt, không thêm tiêu đề, không gạch đầu dòng, không lời chào hỏi.
"""
    return prompt.strip()
