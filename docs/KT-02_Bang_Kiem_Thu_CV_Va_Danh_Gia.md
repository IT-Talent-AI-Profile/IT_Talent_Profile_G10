# BẢNG KẾT QUẢ KIỂM THỬ CV VÀ ĐÁNH GIÁ NĂNG LỰC [KT-02]

**Dự án:** IT Talent AI Profile (Nhóm 10)  
**Người thực hiện:** Đỗ Quang Vĩ  
**Mã Task:** KT-02 | **Môn học:** Thực tập doanh nghiệp  
**Ngày thực hiện:** 19/11/2026 | **Phiên bản:** 1.0  
**Tỷ lệ đạt:** 13 / 13 ca (100% ĐẠT)  

---

### BẢNG KỊCH BẢN VÀ KẾT QUẢ KIỂM THỬ CHI TIẾT (13 CA KIỂM THỬ THEO DOD)

| STT | Mã Ca | Kịch bản kiểm thử | Dữ liệu đầu vào (Input) | Kết quả mong đợi (Expected) | Kết quả thực tế (Actual) | Đánh giá |
|:---:|:---:|:---|:---|:---|:---|:---:|
| **01** | `TC-CV-01` | **File văn bản .txt đổi đuôi thành .pdf** | File văn bản thô đổi tên `fake.pdf` không có cấu trúc chuẩn PDF | Bị từ chối với HTTP 400 Bad Request, báo lỗi định dạng PDF không hợp lệ | HTTP 400, detail `"Chỉ chấp nhận tệp PDF hợp lệ"` | **ĐẠT** |
| **02** | `TC-CV-02` | **Tải lên file CV dung lượng vượt quá 5 MB** | File PDF dung lượng > 5 MB (5.1 MB) | Trả về HTTP 413 Payload Too Large, chặn tại tầng đọc stream không nạp RAM | HTTP 413, detail `"Dung lượng CV không được vượt quá 5 MB"` | **ĐẠT** |
| **03** | `TC-CV-03` | **Tải lên PDF dạng ảnh quét (Scanned PDF)** | File PDF trắng hoặc scan ảnh không có text stream | Ghi nhận trạng thái `failed`, thông báo không trích xuất được văn bản và gợi ý nhập tay | HTTP 200, `status: "failed"`, `error_message: "Không trích xuất được văn bản..."` | **ĐẠT** |
| **04** | `TC-CV-04` | **Xử lý sự cố AI mất mạng hoặc API Timeout** | Giả lập ngoại lệ Timeout khi gọi LLM | Bắt lỗi an toàn, lưu bản ghi `failed`, giao diện hiển thị nút nhập hồ sơ thủ công | HTTP 200, `status: "failed"`, bắt ngoại lệ an toàn, không crash server | **ĐẠT** |
| **05** | `TC-CV-05` | **Ứng viên xem kết quả CV của người khác** | Token ứng viên B gọi `GET /cv/{cv_a_id}` của ứng viên A | Trả về HTTP 404 Not Found, không lộ thông tin CV giữa các ứng viên | HTTP 404, detail `"Không tìm thấy CV hoặc bạn không có quyền truy cập"` | **ĐẠT** |
| **06** | `TC-CV-06` | **Xác nhận kết quả CV hai lần (Confirm CV)** | Gửi yêu cầu xác nhận `POST /cv/{id}/confirm` 2 lần liên tiếp | Cập nhật hồ sơ an toàn, tính lại điểm đánh giá chuẩn xác, không gây lỗi DB | HTTP 200, hồ sơ cập nhật thành công, `status: confirmed` | **ĐẠT** |
| **07** | `TC-EVAL-01` | **Xếp cấp độ với 5 năm kinh nghiệm và 75 điểm** | `years_experience = 5.0`, `total_score = 75.0` | Đạt cả 2 điều kiện ($\ge 5$ năm và $\ge 75$ điểm) $\rightarrow$ Xếp cấp độ **Senior** | Kết quả trả về: `"Senior"` | **ĐẠT** |
| **08** | `TC-EVAL-02` | **Xếp cấp độ với 4.9 năm kinh nghiệm và 90 điểm** | `years_experience = 4.9`, `total_score = 90.0` | Điểm rất cao ($\ge 75$) nhưng chưa đủ 5 năm kinh nghiệm $\rightarrow$ Xếp cấp độ **Middle** | Kết quả trả về: `"Middle"` | **ĐẠT** |
| **09** | `TC-EVAL-03` | **Hồ sơ không có kỹ năng nào** | Profile rỗng, chưa gắn kỹ năng | Điểm tổng = 0, danh sách nhóm rỗng, xếp cấp độ **Intern** | `total_score: 0`, `groups: {}`, `level: "Intern"` | **ĐẠT** |
| **10** | `TC-EVAL-04` | **Hồ sơ chỉ có kỹ năng thuộc 1 nhóm chuyên môn** | 1 kỹ năng Backend (Proficiency 3, 1 năm EXP) | Điểm nhóm: $3 \times 12 + 1 \times 8 = 44$ điểm; Tổng điểm = 44, xếp **Junior** | `groups: {"Backend": 44.0}`, `total_score: 44.0`, `level: "Junior"` | **ĐẠT** |
| **11** | `TC-EVAL-05` | **Hồ sơ có kỹ năng thuộc nhiều nhóm (Đa nhóm)** | Python (Backend - 68đ), React (Frontend - 68đ) | Điểm tổng = Trung bình cộng các nhóm $= (68 + 68) / 2 = 68.0$, xếp **Middle** | `groups: {"Backend": 68.0, "Frontend": 68.0}`, `total_score: 68.0`, `level: "Middle"` | **ĐẠT** |
| **12** | `TC-EVAL-06` | **Proficiency mức 5 và 5 năm kinh nghiệm** | `proficiency = 5`, `years_used = 5.0` | Công thức: $5 \times 12 + 5 \times 8 = 60 + 40 = 100$ điểm trọn vẹn | Kết quả trả về: `100.0` điểm | **ĐẠT** |
| **13** | `TC-EVAL-07` | **Kỹ năng có số năm sử dụng lớn hơn 5 năm** | `proficiency = 5`, `years_used = 8.0` (> 5 năm) | Số năm được giới hạn trần $\min(8, 5) = 5$, điểm tối đa không vượt quá 100 | Kết quả trả về: `100.0` điểm (không bị tràn điểm) | **ĐẠT** |

---

### MINH CHỨNG TỰ ĐỘNG HÓA (AUTOMATED TEST SUITE)

Tất cả 13 ca kiểm thử trên được kiểm chứng và tự động hóa 100% qua 4 bộ test suite bằng `pytest`:
* `backend/tests/test_pdf_parser.py` (9 tests) - Kiểm thử trích xuất chữ trong PDF, từ chối file quá 5MB, phát hiện PDF ảnh quét.
* `backend/tests/test_cv.py` (6 tests) - Kiểm thử toàn trình luồng upload CV, trích xuất AI, phân quyền và xác nhận vào hồ sơ.
* `backend/tests/test_evaluation.py` (13 tests) - Kiểm thử công thức tính điểm kỹ năng, điểm nhóm, ngưỡng cấp độ Intern/Junior/Middle/Senior.
* `backend/tests/test_kt02_cv_evaluation.py` (13 tests) - Kiểm thử chuyên biệt 13 ca theo đúng bảng đặc tả DoD của KT-02.

**Tổng số test tự động thực thi:** **41 / 41 passed (100% ĐẠT)**  
**Thời gian thực thi:** **< 2.5 giây**
