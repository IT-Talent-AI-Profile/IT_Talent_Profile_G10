# IT Talent AI Profile — Project structure

Bộ khung thư mục khởi tạo cho dự án theo SRS, System Design và Product Backlog V3.

- `backend/`: FastAPI, SQLAlchemy, Pydantic, JWT, xử lý PDF, AI, đánh giá và matching.
- `frontend/`: HTML, CSS, vanilla JavaScript dùng Fetch API.
- `database/`: schema MySQL và dữ liệu kỹ năng mẫu.
- `docs/`: tài liệu dự án; thêm tài liệu gốc khi cần.
- `scripts/`: các script hỗ trợ chạy/thử nghiệm.

**Lưu ý:** Đây là bước tạo cây thư mục; các file `.py`, `.html`, `.css`, `.js`, `.sql` là placeholder và chưa có logic chạy.

**Phân công từ Backlog V3:** Vĩ phụ trách nền FastAPI/JWT/AI/CV/evaluation; Sang phụ trách models/schemas, nền frontend, jobs/matching; Đức phụ trách DB/seed, auth và UI profile/evaluation. Phân công chi tiết xem backlog để tránh đụng code.
