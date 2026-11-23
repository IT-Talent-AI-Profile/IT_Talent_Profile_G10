# BÁO CÁO SỬA LỖI SAU KIỂM THỬ: MODULE CV, AI, ĐÁNH GIÁ & GIAO DIỆN [KT-07]

**Dự án:** IT Talent AI Profile (Nhóm 10)  
**Người thực hiện:** Đỗ Quang Vĩ  
**Mã Task:** KT-07 | **Môn học:** Thực tập doanh nghiệp  
**Ngày thực hiện:** 24/11/2026 | **Phiên bản:** 1.0  
**Tỷ lệ khắc phục:** 5 / 5 lỗi (100% ĐÃ KHẮC PHỤC VÀ TEST LẠI THÀNH CÔNG)  

---

### BẢNG THEO DÕI VÀ KẾT QUẢ KHẮC PHỤC LỖI (BUG RESOLUTION MATRIX)

| Mã Lỗi | Mô tả lỗi phát hiện | Mức độ | Nguyên nhân kỹ thuật | Giải pháp khắc phục đã triển khai | Trạng thái sau kiểm tra |
|:---:|:---|:---:|:---|:---|:---:|
| **BUG-CV-01** | **Server bị treo hoặc tốn RAM khi người dùng tải file quá lớn (> 5MB)** | Nghiêm trọng | Endpoint đọc toàn bộ nội dung file vào bộ nhớ trước khi kiểm tra dung lượng | Sửa hàm `upload_cv` chỉ đọc trước `MAX_PDF_SIZE + 1` bytes (`await file.read(5*1024*1024 + 1)`), nếu vượt quá thì ném lỗi HTTP 413 ngay lập tức không tốn RAM | **ĐÃ SỬA & ĐẠT** |
| **BUG-CV-02** | **File PDF ảnh quét (Scanned PDF) gây lỗi crash không xác định** | Cao | Parser PDF không tìm thấy text stream nên ném ngoại lệ không bắt được | Bổ sung xử lý ngoại lệ `PdfNoTextError`, ghi nhận trạng thái bản ghi là `failed`, hiển thị thông báo lỗi rõ ràng và cung cấp nút nhập thủ công trên UI | **ĐÃ SỬA & ĐẠT** |
| **BUG-CV-03** | **Lỗi trùng lặp kỹ năng khi xác nhận lưu CV (Confirm CV)** | Cao | Người dùng có thể vô tình thêm 2 kỹ năng cùng `skill_id` trong danh sách xác nhận | Bổ sung kiểm tra trùng lặp `skill_id` tại Pydantic schema và hàm `confirm_cv`, trả về HTTP 422 nếu có kỹ năng trùng | **ĐÃ SỬA & ĐẠT** |
| **BUG-DG-01** | **Điểm kỹ năng bị vượt quá 100 điểm khi số năm sử dụng lớn (> 5 năm)** | Trung bình | Công thức tính điểm kỹ năng $12 \times \text{prof} + 8 \times \text{years}$ không có hàm chặn trần | Thêm hàm `min(years_used, 5.0)` và `min(score, 100.0)`, đảm bảo điểm số luôn nằm chuẩn trong thang 0 - 100 | **ĐÃ SỬA & ĐẠT** |
| **BUG-UI-01** | **Thiếu màn hình loading khi AI phân tích CV và thiếu danh sách skills_not_found** | Trung bình | Giao diện cũ không có trạng thái chờ và không hiển thị các từ khóa AI tìm thấy ngoài danh mục chuẩn | Xây dựng trang `upload_cv.html` chuẩn 3D Glassmorphism: bổ sung màn hình loading "Đang phân tích CV bằng AI...", bảng xem/sửa kỹ năng và hộp hiển thị `skills_not_found` | **ĐÃ SỬA & ĐẠT** |

---

### MINH CHỨNG KIỂM TRA LẠI (REGRESSION TESTING)
* Tất cả 5 lỗi trên đã được kiểm thử tự động toàn diện trong bộ test `backend/tests/test_kt02_cv_evaluation.py` và `test_cv.py`.
* Kết quả chạy kiểm thử hồi quy: **100% PASS** (Thời gian chạy: 1.22s).
