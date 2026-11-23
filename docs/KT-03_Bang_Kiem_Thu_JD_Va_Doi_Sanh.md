# BẢNG KẾT QUẢ KIỂM THỬ TIN TUYỂN DỤNG VÀ ĐỐI SÁNH [KT-03]

**Dự án:** IT Talent AI Profile (Nhóm 10)  
**Người thực hiện:** Văn Phúc Sang  
**Mã Task:** KT-03 | **Môn học:** Thực tập doanh nghiệp  
**Ngày thực hiện:** 20/11/2026 | **Phiên bản:** 1.0  
**Tỷ lệ đạt:** 18 / 18 ca (100% ĐẠT)  

---

### BẢNG KỊCH BẢN VÀ KẾT QUẢ KIỂM THỬ CHI TIẾT (18 CA KIỂM THỬ THEO DOD)

| STT | Mã Ca | Kịch bản kiểm thử | Dữ liệu đầu vào (Input) | Kết quả mong đợi (Expected) | Kết quả thực tế (Actual) | Đánh giá |
|:---:|:---:|:---|:---|:---|:---|:---:|
| **01** | `TC-JD-01` | **Tạo tin tuyển dụng (JD) mới thành công** | `title: "Senior Python Backend Engineer"`, `min_years: 3.5`, `description: "..."` | Trả về HTTP 200, tạo JD mới với `is_open: True`, danh sách skills rỗng ban đầu | HTTP 200, ID sinh tự động, `is_open: True` | **ĐẠT** |
| **02** | `TC-JD-02` | **Tính cô lập dữ liệu giữa các Nhà tuyển dụng** | NTD A và NTD B cùng tạo JD; gọi `GET /jobs` từ từng tài khoản | NTD A chỉ xem được JD của A; NTD B chỉ xem được JD của B | Danh sách hoàn toàn riêng biệt, không lộ thông tin chéo | **ĐẠT** |
| **03** | `TC-JD-03` | **NTD A truy cập hoặc thao tác trên JD của NTD B** | Gửi yêu cầu xem/sửa `GET /jobs/{job_b_id}` bằng token của NTD A | Trả về HTTP 404 Not Found, không tìm thấy JD hoặc không có quyền | HTTP 404, detail `"Không tìm thấy JD"` | **ĐẠT** |
| **04** | `TC-JD-04` | **Cập nhật thông tin JD** | `PUT /jobs/{id}` với tiêu đề mới, mô tả mới, `min_years: 3.0` | Trả về HTTP 200 kèm JD đã được cập nhật dữ liệu mới chính xác | HTTP 200, dữ liệu cập nhật khớp 100% | **ĐẠT** |
| **05** | `TC-JD-05` | **Đóng và Mở lại trạng thái tin tuyển dụng hai chiều** | Gọi API đổi `is_open: False` (Đóng tin), sau đó gọi `is_open: True` (Mở lại tin) | Trạng thái `is_open` thay đổi tương ứng cả 2 chiều trong CSDL | HTTP 200, `is_open` chuyển mượt mà giữa True và False | **ĐẠT** |
| **06** | `TC-JD-06` | **Gắn kỹ năng yêu cầu / ưu tiên vào JD** | `POST /jobs/{id}/skills` với `skill_id: 1`, `is_required: True` | Trả về HTTP 200 kèm danh sách kỹ năng đã gắn cho JD | HTTP 200, kỹ năng được lưu vào bảng `job_skills` | **ĐẠT** |
| **07** | `TC-JD-07` | **Gắn kỹ năng trùng lặp vào JD (Upsert)** | Gắn lại `skill_id: 1` nhưng đổi `is_required: False` | Cập nhật cờ `is_required`, không tạo thêm dòng mới trùng lặp trong DB | HTTP 200, số lượng kỹ năng không tăng, `is_required: False` | **ĐẠT** |
| **08** | `TC-JD-08` | **Gắn kỹ năng không tồn tại trong danh mục** | `POST /jobs/{id}/skills` với `skill_id: 999999` | Trả về HTTP 404 Not Found, báo lỗi kỹ năng không tồn tại | HTTP 404, detail `"Kỹ năng không tồn tại"` | **ĐẠT** |
| **09** | `TC-JD-09` | **Gỡ kỹ năng khỏi JD** | `DELETE /jobs/{id}/skills/{skill_id}` | Xóa thành công kỹ năng khỏi JD, trả về danh sách kỹ năng đã cập nhật | HTTP 200, kỹ năng bị loại bỏ khỏi danh sách | **ĐẠT** |
| **10** | `TC-JD-10` | **Xóa tin tuyển dụng (Cascade xóa quan hệ)** | `DELETE /jobs/{id}` | Xóa thành công JD và tự động cascade xóa sạch các liên kết trong `job_skills` | HTTP 200, bản ghi JD và các liên kết skill bị xóa hoàn toàn | **ĐẠT** |
| **11** | `TC-MATCH-01` | **Chưa đăng nhập gọi API đối sánh ứng viên** | `GET /jobs/{id}/matches` không kèm Header Authorization | Trả về HTTP 401 Unauthorized | HTTP 401 Unauthorized | **ĐẠT** |
| **12** | `TC-MATCH-02` | **Ứng viên gọi API đối sánh (Role Isolation)** | Gửi token của Ứng viên (role: candidate) vào `GET /jobs/{id}/matches` | Trả về HTTP 403 Forbidden, chỉ cho phép Nhà tuyển dụng truy cập | HTTP 403, detail `"Chỉ dành cho Nhà tuyển dụng"` | **ĐẠT** |
| **13** | `TC-MATCH-03` | **Gọi đối sánh với JD không tồn tại hoặc của NTD khác** | `GET /jobs/99999/matches` bằng token của NTD | Trả về HTTP 404 Not Found, `"Tin tuyển dụng không tồn tại"` | HTTP 404, detail `"Tin tuyển dụng không tồn tại"` | **ĐẠT** |
| **14** | `TC-MATCH-04` | **Gọi đối sánh cho tin tuyển dụng đã đóng (is_open = False)** | `GET /jobs/{closed_job_id}/matches` khi JD đã đóng | Trả về HTTP 400 Bad Request, `"Tin tuyển dụng đã đóng"` (theo đúng DoD) | HTTP 400, detail `"Tin tuyển dụng đã đóng"` | **ĐẠT** |
| **15** | `TC-MATCH-05` | **Lọc và ẩn tuyệt đối hồ sơ riêng tư (is_public = False)** | Hồ sơ có kỹ năng khớp 100% nhưng đặt `is_public: False` | Tuyệt đối không xuất hiện trong danh sách đối sánh của bất kỳ JD nào | Profile riêng tư bị loại bỏ 100% khỏi kết quả | **ĐẠT** |
| **16** | `TC-MATCH-06` | **Xếp hạng ứng viên giảm dần theo % độ phù hợp và điểm AI** | Tập ứng viên với độ khớp 100%, 75%, 50%, 0% | Danh sách trả về được sắp xếp giảm dần theo `%` khớp, tiếp đến `total_score`, sau đó `id` | Thứ tự trả về: 100% -> 75% -> 50% -> 0% chính xác | **ĐẠT** |
| **17** | `TC-MATCH-07` | **Thuật toán đối sánh kỹ năng và phân loại khớp / thiếu** | JD yêu cầu Python, SQL; Ưu tiên Docker. Ứng viên có Python (4★), SQL (2★) | Mức proficiency >= 3 tính là khớp, < 3 tính là thiếu; phân chia `matched_skills` và `missing_skills` chuẩn xác | Python thuộc matched, SQL và Docker thuộc missing; % khớp tính đúng | **ĐẠT** |
| **18** | `TC-MATCH-08` | **Phân trang kết quả đối sánh (Pagination)** | Tạo 15 ứng viên công khai, gọi `page=1` và `page=2` (pageSize=10) | Trang 1 trả về 10 ứng viên đầu bảng, trang 2 trả về 5 ứng viên tiếp theo, `total: 15` | Trang 1: 10 ứng viên; Trang 2: 5 ứng viên; không trùng lặp | **ĐẠT** |

---

### MINH CHỨNG TỰ ĐỘNG HÓA (AUTOMATED TEST SUITE)

Tất cả 18 ca kiểm thử trên được bao phủ toàn diện và tự động hóa 100% qua 4 bộ test suite bằng `pytest`:
* `backend/tests/test_jobs.py` (17 tests) - Kiểm thử CRUD JD, quyền truy cập, phân quyền role, gắn/gỡ kỹ năng, tính cô lập.
* `backend/tests/test_matching.py` (9 tests) - Kiểm thử thuật toán tính toán độ khớp, trọng số bắt buộc/ưu tiên, ngưỡng năng lực proficiency.
* `backend/tests/test_candidates.py` (8 tests) - Kiểm thử tìm kiếm ứng viên, lọc đa kỹ năng, lọc cấp độ, chi tiết hồ sơ.
* `backend/tests/test_matches_ds02.py` (8 tests) - Kiểm thử phân quyền 401/403, 404 JD khác, 400 JD đóng, ẩn hồ sơ private, sắp xếp giảm dần và phân trang.

**Tổng số test tự động thực thi:** **42 / 42 passed (100% ĐẠT)**  
**Thời gian thực thi:** **2.43 giây**
