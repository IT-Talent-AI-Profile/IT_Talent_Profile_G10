"""
Script generate_demo_cvs.py (Task TL-03 - Phụ trách: Vĩ)
Tạo 3 file CV PDF mẫu phục vụ buổi thuyết trình Demo:
1. CV_Senior_Python_Backend.pdf (Senior: Python, FastAPI, MySQL, Docker, Redis - 6 năm EXP)
2. CV_Middle_Frontend_React.pdf (Middle: React, TypeScript, JavaScript, CSS, RESTful API - 3 năm EXP)
3. CV_Junior_Fullstack_Dev.pdf (Junior: Node.js, Express, MongoDB, Vue.js, Git - 1.5 năm EXP)
"""
from pathlib import Path
import sys

# Thêm đường dẫn backend để import hàm tạo PDF
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from tests.test_pdf_parser import create_text_pdf

OUTPUT_DIR = Path(__file__).resolve().parents[2] / "docs" / "demo_samples"


def generate_cvs():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    cv_senior_text = [
        "HO SO UNG VIEN - NGUYEN VAN SENIOR",
        "Vi tri mong muon: Senior Backend Engineer | Kinh nghiem: 6.0 nam",
        "Hoc van: Dai hoc Bach Khoa Ha Noi - Ky su CNTT",
        "Kinh nghiem lam viec: 6 nam phat trien he thong Backend chiu tai cao, Microservices va Distributed Systems",
        "Ky nang chuyen mon: Python, FastAPI, MySQL, Docker, Redis, RESTful API, System Design, Git",
        "Du an tieu bieu: Core Banking Gateway, High-volume E-commerce Microservices Architecture"
    ]

    cv_middle_text = [
        "HO SO UNG VIEN - TRAN THI MIDDLE",
        "Vi tri mong muon: Frontend Developer | Kinh nghiem: 3.0 nam",
        "Hoc van: Dai hoc Khoa hoc Tu nhien - Cu nhan CNTT",
        "Kinh nghiem lam viec: 3 nam lap trinh Single Page Applications (SPA), responsive web va toi uu UI/UX",
        "Ky nang chuyen mon: React, TypeScript, JavaScript, HTML5, CSS3, Redux, RESTful API, TailwindCSS, Git",
        "Du an tieu bieu: SaaS Enterprise Dashboard, Customer Portal Web Application"
    ]

    cv_junior_text = [
        "HO SO UNG VIEN - LE VAN JUNIOR",
        "Vi tri mong muon: Fullstack Developer | Kinh nghiem: 1.5 nam",
        "Hoc van: Dai hoc Cong nghe - DHQG Ha Noi",
        "Kinh nghiem lam viec: 1.5 nam tham gia xay dung REST API va giao dien web cho du an startup",
        "Ky nang chuyen mon: Node.js, Express, MongoDB, Vue.js, JavaScript, Git, Docker co ban",
        "Du an tieu bieu: Realtime Chat Web Application, Internal Booking Management System"
    ]

    cvs = [
        ("CV_Senior_Python_Backend.pdf", cv_senior_text),
        ("CV_Middle_Frontend_React.pdf", cv_middle_text),
        ("CV_Junior_Fullstack_Dev.pdf", cv_junior_text)
    ]

    for filename, pages in cvs:
        # Gom các dòng thành đoạn text có phân dòng cho PDF stream
        pdf_bytes = create_text_pdf(["\n".join(pages)])
        target_path = OUTPUT_DIR / filename
        target_path.write_bytes(pdf_bytes)
        print(f"[OK] Đã tạo thành công: {target_path} ({len(pdf_bytes)} bytes)")


if __name__ == "__main__":
    generate_cvs()
