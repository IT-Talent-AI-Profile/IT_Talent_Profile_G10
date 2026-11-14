# 🚀 IT Talent AI Profile — Hệ Thống Hồ Sơ Năng Lực IT Tích Hợp AI (Nhóm 10)

> **Môn học:** Thực tập doanh nghiệp (01) — Lớp: `HCM-KS25-CNTT6`  
> **Mentor phụ trách:** Nguyễn Hữu Minh Dương  
> **Nhóm thực hiện:** Nhóm 10  
> * **Võ Chí Đức** (Leader) — MSSV: `PTIT-HCM-055`
> * **Đỗ Quang Vĩ** — MSSV: `N25DTCN074`
> * **Văn Phúc Sang** — MSSV: `N25DTCN048`

---

## 📖 1. Giới thiệu tổng quan
**IT Talent AI Profile** là nền tảng quản lý và đánh giá hồ sơ năng lực dành cho nhân sự ngành Công nghệ Thông tin, ứng dụng mô hình ngôn ngữ lớn (Claude 3.5 Sonnet) để tự động trích xuất thông tin từ CV, đánh giá điểm mạnh - điểm yếu và đối sánh tự động giữa hồ sơ ứng viên với các vị trí tuyển dụng (JD).

### 🌟 Tính năng nổi bật đã hoàn thành:
1. **Phân quyền và bảo mật (Auth):** Mã hóa mật khẩu Bcrypt, xác thực JWT Token, phân tách quyền hạn chặt chẽ giữa Ứng viên (`candidate`) và Nhà tuyển dụng (`recruiter`).
2. **Hồ sơ năng lực 3D (3D Profile & Roadmap):** Giao diện thẻ 3D Tilt Card tương tác, viền LED Conic Gradient, thước đo lộ trình thăng tiến sự nghiệp từ *Intern* lên *Senior*.
3. **Quản lý 60 Kỹ năng chuẩn IT:** Chuẩn hóa kỹ năng theo 6 nhóm chuyên môn, chấm điểm 1-5 sao trực quan, đồng bộ tức thì vào cơ sở dữ liệu MySQL.
4. **Trí tuệ nhân tạo Claude LLM:** Đánh giá năng lực tự động, tóm tắt điểm mạnh và khuyến nghị phát triển chuyên môn dưới 150 từ bằng tiếng Việt chuẩn UTF-8.
5. **Trung tâm Nhà tuyển dụng (JD & AI Match):** Quản lý trạng thái tin tuyển dụng, thuật toán đối sánh độ phù hợp (Match Score %) giữa ứng viên và JD theo thang điểm 60% bắt buộc + 20% ưu tiên + 20% số năm kinh nghiệm.
6. **Xóa tài khoản & hồ sơ (HS-04):** Xóa sạch file PDF CV trên ổ cứng và tự động xóa dây chuyền (CASCADE) toàn bộ dữ liệu người dùng.

---

## 🛠️ 2. Yêu cầu môi trường cài đặt (Prerequisites)
* **Hệ điều hành:** Windows 10/11, macOS, hoặc Linux (Ubuntu 20.04+)
* **Python:** Phiên bản `3.11` trở lên (Khuyến nghị 3.11 hoặc 3.12)
* **MySQL Server:** Phiên bản `8.0` trở lên
* **Trình duyệt:** Chrome, Edge, Safari hoặc Firefox phiên bản mới nhất

---

## 🗄️ 3. Thiết lập Cơ sở dữ liệu MySQL
1. Khởi động MySQL Server (qua XAMPP, MySQL Workbench hoặc MySQL CLI).
2. Tạo database mới với bảng mã UTF-8:
   ```sql
   CREATE DATABASE it_talent_ai CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   ```
3. Nạp dữ liệu theo đúng thứ tự 3 file SQL trong thư mục `database/`:
   ```bash
   # Bước 1: Khởi tạo 7 bảng và 3 chỉ mục Index
   mysql -u root -p it_talent_ai < database/schema.sql

   # Bước 2: Nạp 60 kỹ năng chuẩn IT phân loại 6 nhóm
   mysql -u root -p it_talent_ai < database/seed_skills.sql

   # Bước 3: Nạp dữ liệu mẫu để chạy thử nghiệm và kiểm thử
   mysql -u root -p it_talent_ai < database/sample_data.sql
   ```

---

## ⚙️ 4. Cài đặt và Khởi chạy Backend (FastAPI)

### Bước 4.1: Tạo môi trường ảo và cài đặt thư viện
Mở Terminal tại thư mục `backend/`:
```bash
cd backend

# Tạo môi trường ảo (Khuyến nghị)
python -m venv venv

# Kích hoạt môi trường ảo:
# Trên Windows:
.\venv\Scripts\activate
# Trên macOS / Linux:
source venv/bin/activate

# Cài đặt toàn bộ thư viện cần thiết
pip install -r requirements.txt
```

### Bước 4.2: Cấu hình biến môi trường (`.env`)
Tạo file `.env` tại thư mục `backend/` từ mẫu `.env.example`:
```ini
# Kết nối MySQL
DATABASE_URL=mysql+pymysql://root:password@127.0.0.1:3306/it_talent_ai?charset=utf8mb4

# Bảo mật JWT
SECRET_KEY=it_talent_ai_super_secret_jwt_key_2026_at_least_32_bytes_long!
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

# Cấu hình AI Client (Claude LLM)
ANTHROPIC_API_KEY=your_anthropic_api_key_here
AI_MODE=mock  # Chọn 'mock' để chạy offline hoặc 'real' khi có API Key
```

### Bước 4.3: Khởi chạy Server
```bash
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```
* **Swagger UI (Tài liệu API tương tác):** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
* **ReDoc:** [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

---

## 💻 5. Khởi chạy Giao diện Frontend
Frontend được thiết kế theo cấu trúc Static Web hiện đại, không cần build nặng nề:
1. Mở file `frontend/login.html` trực tiếp bằng trình duyệt Chrome/Edge hoặc dùng tiện ích **Live Server** trong VS Code.
2. Các trang chính của hệ thống:
   * **`frontend/login.html`**: Trang Đăng nhập & Đăng ký phân quyền (tích hợp nút chọn 1 chạm tài khoản mẫu).
   * **`frontend/profile.html`**: Trang Hồ sơ năng lực 3D, Lộ trình nghề nghiệp, Quản lý 60 kỹ năng và Vùng nguy hiểm xóa tài khoản.
   * **`frontend/jobs.html`**: Trung tâm Quản lý tin tuyển dụng & Đối sánh ứng viên AI dành cho Nhà tuyển dụng.
   * **`frontend/demo_video.html`**: Trình phát Video mô phỏng tương tác 60fps toàn bộ 6 chức năng.

---

## 🔑 6. Danh sách Tài khoản mẫu dùng để Test (1 Chạm)

| Vai trò | Email đăng nhập | Mật khẩu | Ghi chú |
| :--- | :--- | :---: | :--- |
| **Ứng viên (Candidate)** | `chiducofficial@gmail.com` | `12345678` | Tài khoản Võ Chí Đức, có sẵn hồ sơ 3D và 12 kỹ năng |
| **Ứng viên (Senior)** | `nguyen.senior@example.com` | `12345678` | Đạt cấp độ Senior, đã hoàn tất tóm tắt AI |
| **Nhà tuyển dụng (Recruiter)** | `hr@fpt.com` | `12345678` | FPT Software, có sẵn các tin tuyển dụng đang mở |
| **Nhà tuyển dụng (VNG)** | `tuyendung@vng.com` | `12345678` | VNG Corporation, vị trí Fullstack & DevOps |

---

## 🧪 7. Chạy Kiểm thử Tự động (Automated Test Suite)
Hệ thống tích hợp bộ kiểm thử toàn diện với pytest kiểm tra chặt chẽ toàn bộ logic nghiệp vụ và quyền truy cập:

```bash
cd backend
pytest tests/
```
**Kết quả kiểm thử:**
$$\mathbf{88 / 88\ tests\ PASSED}\ (100\%)$$
* `test_auth.py`: Kiểm tra băm Bcrypt, token JWT, đăng ký, đăng nhập.
* `test_auth_dependencies_integration.py` & `test_dependencies.py`: Kiểm tra bảo vệ route theo role.
* `test_profiles.py`: Kiểm tra xem, sửa hồ sơ, quản lý kỹ năng, và xóa tài khoản cascade (HS-04).
* `test_jobs.py`: Kiểm tra CRUD tin tuyển dụng, gắn/gỡ kỹ năng, phân quyền dữ liệu giữa các NTD.
* `test_matching.py`: Kiểm tra thuật toán đối sánh độ phù hợp (DS-01).
* `test_pdf_parser.py`: Kiểm tra đọc và kiểm tra tính hợp lệ của file PDF CV (CV-01).
* `test_ai_client.py`: Kiểm tra prompt và kết nối Claude API (Mock & Real).

---

## 📂 8. Cấu trúc thư mục dự án

```text
IT_Talent_AI_Profile_Code/
├── backend/
│   ├── app/
│   │   ├── api/             # Các Router API (auth, profiles, jobs, cv, evaluation, matching)
│   │   ├── core/            # Config, bảo mật JWT, dependencies phân quyền
│   │   ├── db/              # Kết nối SQLAlchemy Session và Base model
│   │   ├── models/          # 7 bảng cơ sở dữ liệu (User, Profile, Skill, Job, v.v.)
│   │   ├── schemas/         # Pydantic schemas validate dữ liệu
│   │   ├── services/        # Logic nghiệp vụ (auth, profile, job, matching, ai_client)
│   │   └── utils/           # Tiện ích đọc PDF (pdf_parser)
│   ├── tests/               # 88 ca kiểm thử tự động pytest
│   ├── requirements.txt     # Danh sách thư viện Python
│   └── .env.example         # File mẫu cấu hình biến môi trường
├── database/                # Mã nguồn SQL (schema.sql, seed_skills.sql, sample_data.sql)
├── docs/                    # Tài liệu kỹ thuật & Bảng kiểm thử (KT-01)
├── frontend/                # Giao diện người dùng HTML/CSS/JS (login, profile, jobs, demo)
└── README.md                # Hướng dẫn chi tiết cài đặt và sử dụng
```

---
*Chúc bạn có trải nghiệm tuyệt vời cùng hệ thống **IT Talent AI Profile**!*
