# BẢNG KẾT QUẢ KIỂM THỬ TÀI KHOẢN VÀ HỒ SƠ [KT-01]

**Dự án:** IT Talent AI Profile (Nhóm 10)  
**Người thực hiện:** Võ Chí Đức (Leader)  
**Mã Task:** KT-01 | **Môn học:** Thực tập doanh nghiệp  
**Ngày thực hiện:** 14/11/2026 | **Phiên bản:** 1.0  
**Tỷ lệ đạt:** 14 / 14 ca (100% ĐẠT)  

---

### BẢNG KỊCH BẢN VÀ KẾT QUẢ KIỂM THỬ CHI TIẾT (14 CA KIỂM THỬ THEO DOD)

| STT | Mã Ca | Kịch bản kiểm thử | Dữ liệu đầu vào (Input) | Kết quả mong đợi (Expected) | Kết quả thực tế (Actual) | Đánh giá |
|:---:|:---:|:---|:---|:---|:---|:---:|
| **01** | `TC-AUTH-01` | **Đăng ký tài khoản mới thành công** | Email chưa tồn tại, mật khẩu `valid_password_123`, role: `candidate` | Trả về HTTP 200, message `"Đăng ký thành công"`, tạo bản ghi trong DB | HTTP 200, message `"Đăng ký thành công"` | **ĐẠT** |
| **02** | `TC-AUTH-02` | **Đăng ký với email đã tồn tại (Trùng email)** | Email đã có trong hệ thống | Trả về HTTP 400, báo lỗi `"Email đã được đăng ký"` | HTTP 400, detail `"Email đã được đăng ký"` | **ĐẠT** |
| **03** | `TC-AUTH-03` | **Đăng ký với mật khẩu ngắn (< 8 ký tự)** | Password: `"12345"` (5 ký tự) | Trả về HTTP 422 Unprocessable Entity, validation schema chặn lại | HTTP 422, String should have at least 8 characters | **ĐẠT** |
| **04** | `TC-AUTH-04` | **Đăng ký với sai vai trò (Invalid Role)** | Role: `"superadmin"` hoặc role không thuộc `candidate`/`recruiter` | Trả về HTTP 422, từ chối giá trị role không hợp lệ | HTTP 422, Input should be 'candidate' or 'recruiter' | **ĐẠT** |
| **05** | `TC-AUTH-05` | **Đăng nhập đúng tài khoản và mật khẩu** | Email mẫu `nguyen.senior@example.com`, mật khẩu `12345678` | Trả về HTTP 200, chuỗi JWT token hợp lệ, role: `candidate` | HTTP 200, nhận đủ `token` và `role` | **ĐẠT** |
| **06** | `TC-AUTH-06` | **Đăng nhập sai mật khẩu** | Email đúng, mật khẩu `"wrongpassword"` | Trả về HTTP 401 Unauthorized, thông báo `"Email hoặc mật khẩu không đúng"` | HTTP 401, detail `"Email hoặc mật khẩu không đúng"` | **ĐẠT** |
| **07** | `TC-AUTH-07` | **Xác thực token JWT hết hạn** | Token đã tạo với thời gian hết hạn trong quá khứ (`expires_minutes=-1`) | Hệ thống từ chối xác thực, ném lỗi token hết hạn (HTTP 401) | HTTP 401 / ValueError Token đã hết hạn | **ĐẠT** |
| **08** | `TC-AUTH-08` | **Ứng viên gọi API của Nhà tuyển dụng (Role Isolation)** | Gửi token Candidate vào các API `/jobs` hoặc `/jobs/create` | Trả về HTTP 403 Forbidden, thông báo phân quyền rõ ràng | HTTP 403, detail `"Chỉ dành cho Nhà tuyển dụng"` | **ĐẠT** |
| **09** | `TC-PRF-01` | **Cập nhật thông tin hồ sơ cá nhân** | `PUT /profiles/me` với full_name, desired_position, years_experience: 3.5 | Trả về HTTP 200 kèm hồ sơ đã cập nhật, GET lại hiển thị đúng | HTTP 200, dữ liệu khớp 100% với cập nhật | **ĐẠT** |
| **10** | `TC-PRF-02` | **Thêm kỹ năng trùng vào hồ sơ (Upsert)** | Gắn skill_id đã có sẵn trong profile, đổi proficiency từ 3 lên 5 | Cập nhật mức thành thạo, không tạo thêm dòng mới trùng lặp | HTTP 200, số lượng kỹ năng giữ nguyên, proficiency = 5 | **ĐẠT** |
| **11** | `TC-PRF-03` | **Gắn kỹ năng không tồn tại trong danh mục** | `POST /profiles/me/skills` với `skill_id: 99999` | Trả về HTTP 404 Not Found, `"Kỹ năng không tồn tại trong danh mục"` | HTTP 404, detail `"Kỹ năng không tồn tại trong danh mục"` | **ĐẠT** |
| **12** | `TC-PRF-04` | **Gắn kỹ năng với mức thành thạo sai (Mức 0 và Mức 6)** | `proficiency = 0` hoặc `proficiency = 6` (ngoài khoảng 1-5) | Trả về HTTP 422 Unprocessable Entity, chặn tại tầng Pydantic schema | HTTP 422, Input should be greater than or equal to 1 / less than or equal to 5 | **ĐẠT** |
| **13** | `TC-PRF-05` | **Bật / Tắt trạng thái công khai hồ sơ (is_public)** | Cập nhật `is_public: True` rồi đổi sang `is_public: False` | Trạng thái hiển thị badge trên giao diện và DB thay đổi tương ứng | HTTP 200, `is_public` lưu đúng giá trị boolean | **ĐẠT** |
| **14** | `TC-PRF-06` | **Xóa hồ sơ và tài khoản (CASCADE & Dọn file mồ côi)** | `DELETE /profiles/me` của ứng viên có file CV trong `uploads/` | Xóa sạch file vật lý trong `uploads/`, xóa user, cascade xóa profiles, profile_skills, cv_files | HTTP 200, file CV bị xóa, không còn dòng nào trong DB | **ĐẠT** |

---

### MINH CHỨNG TỰ ĐỘNG HÓA (AUTOMATED TEST SUITE)
Tất cả 14 ca kiểm thử trên đã được tự động hóa hoàn toàn trong 2 file kiểm thử:
* `backend/tests/test_auth.py`
* `backend/tests/test_profiles.py`

Kết quả kiểm thử tự động toàn bộ: **100% PASS** (Thời gian chạy: < 2.0s).
