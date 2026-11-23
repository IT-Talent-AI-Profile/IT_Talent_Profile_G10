# BẢNG KẾT QUẢ KIỂM THỬ HỆ THỐNG TOÀN TRÌNH (END-TO-END) VÀ PHÂN QUYỀN [KT-04]

**Dự án:** IT Talent AI Profile (Nhóm 10)  
**Người thực hiện:** Võ Chí Đức (Leader)  
**Mã Task:** KT-04 | **Môn học:** Thực tập doanh nghiệp  
**Ngày thực hiện:** 24/11/2026 | **Phiên bản:** 1.0  
**Tỷ lệ đạt:** 100% ĐẠT (Không có lỗi chặn)  

---

### 1. KỊCH BẢN KIỂM THỬ TOÀN TRÌNH NGƯỜI DÙNG THẬT (END-TO-END USER JOURNEY)

Hệ thống được kiểm thử tự động và thủ công chạy suốt 2 vòng liên tiếp trên cơ sở dữ liệu sạch:

| Bước | Hành động của người dùng | API gọi tương ứng | Dữ liệu đầu vào | Kết quả thực tế | Đánh giá |
|:---:|:---|:---|:---|:---|:---:|
| **B1** | **Đăng ký tài khoản Ứng viên mới** | `POST /auth/register` | `candidate_e2e@example.com`, pass: `Password123`, role: `candidate` | HTTP 200, tạo tài khoản và tự động khởi tạo bản ghi hồ sơ rỗng | **ĐẠT** |
| **B2** | **Đăng nhập lấy JWT Bearer Token** | `POST /auth/login` | Email + Mật khẩu vừa tạo | HTTP 200, nhận JWT token hợp lệ chứa `user_id`, `role: candidate` | **ĐẠT** |
| **B3** | **Tải lên CV PDF và trích xuất AI** | `POST /cv/upload` | File `my_resume.pdf` (chứa text Senior Python, FastAPI, SQL) | HTTP 200, trích xuất thành công kinh nghiệm, học vấn và 3 kỹ năng chuẩn | **ĐẠT** |
| **B4** | **Xác nhận CV & Bật công khai hồ sơ** | `POST /cv/{id}/confirm`<br>`PUT /profiles/me` | Chọn mức thành thạo 4★, số năm EXP 3.5 năm; đặt `is_public: True` | HTTP 200, lưu dữ liệu vào hồ sơ, gắn kỹ năng vào `profile_skills` | **ĐẠT** |
| **B5** | **Xem báo cáo đánh giá năng lực AI** | `GET /evaluation/me` | Token ứng viên vừa cập nhật | HTTP 200, tổng điểm: 62.0, cấp độ: Middle, tóm tắt AI phân tích rõ ràng | **ĐẠT** |
| **B6** | **Đăng ký & Đăng nhập Nhà tuyển dụng** | `POST /auth/register`<br>`POST /auth/login` | `recruiter_e2e@example.com`, role: `recruiter` | HTTP 200, xác thực vai trò Nhà tuyển dụng hợp lệ | **ĐẠT** |
| **B7** | **NTD tạo tin JD & gắn kỹ năng yêu cầu** | `POST /jobs`<br>`POST /jobs/{id}/skills` | JD *"Senior Python Backend"*, min_years: 2.0; Gắn Python (bắt buộc), SQL (bắt buộc) | HTTP 200, JD ở trạng thái mở `is_open: True`, lưu đầy đủ vào CSDL | **ĐẠT** |
| **B8** | **Chạy thuật toán đối sánh xếp hạng AI** | `GET /jobs/{id}/matches` | Token NTD gọi đối sánh cho JD vừa tạo | HTTP 200, ứng viên vừa tạo xuất hiện ở Top 1 với độ khớp $\ge 70\%$, đủ matched skills | **ĐẠT** |

---

### 2. MA TRẬN KIỂM TRA PHÂN QUYỀN BẢO MẬT (ROLE & ACCESS ISOLATION)

| STT | Tình huống kiểm thử bảo mật | Phương thức & Endpoint | Quyền hạn gọi | Kết quả mong đợi | Kết quả thực tế | Đánh giá |
|:---:|:---|:---|:---:|:---:|:---:|:---:|
| **01** | Chưa đăng nhập gọi API hồ sơ cá nhân | `GET /profiles/me` | Khách vãng lai | HTTP 401/403 Từ chối truy cập | HTTP 401/403 Unauthorized | **ĐẠT** |
| **02** | Chưa đăng nhập gọi API danh sách tin tuyển dụng | `GET /jobs` | Khách vãng lai | HTTP 401/403 Từ chối truy cập | HTTP 401/403 Unauthorized | **ĐẠT** |
| **03** | Chưa đăng nhập gọi API tìm kiếm ứng viên | `GET /candidates` | Khách vãng lai | HTTP 401/403 Từ chối truy cập | HTTP 401/403 Unauthorized | **ĐẠT** |
| **04** | Gửi token không hợp lệ hoặc đã hết hạn | `GET /profiles/me` | Bearer invalid_token | HTTP 401 Báo lỗi token | HTTP 401 Unauthorized | **ĐẠT** |
| **05** | Ứng viên gọi API tạo tin tuyển dụng của NTD | `POST /jobs` | Token Candidate | HTTP 403 Forbidden | HTTP 403 Forbidden | **ĐẠT** |
| **06** | Ứng viên gọi API xem danh sách đối sánh JD | `GET /jobs/{id}/matches` | Token Candidate | HTTP 403 Forbidden | HTTP 403 Forbidden | **ĐẠT** |
| **07** | NTD A xem / sửa / đối sánh JD của NTD B | `GET /jobs/{job_b_id}` | Token NTD A | HTTP 404 Không tìm thấy JD | HTTP 404 Not Found | **ĐẠT** |
| **08** | Ứng viên A xem kết quả tải CV của Ứng viên B | `GET /cv/{cv_b_id}` | Token Ứng viên A | HTTP 404 Không tìm thấy CV | HTTP 404 Not Found | **ĐẠT** |

---

### 3. ĐỐI SOÁT HỢP ĐỒNG API (24 APIS KHỚP 100% VỚI SWAGGER /DOCS)

Hệ thống tích hợp 8 Router chính trên FastAPI `/docs`, bao phủ đầy đủ 24 API nghiệp vụ:
1. `POST /auth/register` — Đăng ký tài khoản (candidate/recruiter)
2. `POST /auth/login` — Đăng nhập xác thực và cấp JWT
3. `GET /auth/me` — Lấy thông tin tài khoản đang đăng nhập
4. `GET /auth/check-recruiter` — Kiểm tra phân quyền Nhà tuyển dụng
5. `GET /profiles/me` — Xem chi tiết hồ sơ cá nhân
6. `PUT /profiles/me` — Cập nhật thông tin hồ sơ và trạng thái công khai
7. `DELETE /profiles/me` — Xóa tài khoản, hồ sơ và file CV vật lý (Cascade)
8. `POST /profiles/me/skills` — Thêm/cập nhật kỹ năng vào hồ sơ
9. `DELETE /profiles/me/skills/{skill_id}` — Gỡ kỹ năng khỏi hồ sơ
10. `GET /skills` — Lấy danh mục 60 kỹ năng chuẩn IT phân loại 6 nhóm
11. `POST /cv/upload` — Tải lên file CV PDF và phân tích bằng AI
12. `GET /cv/{cv_id}` — Xem kết quả phân tích CV đã lưu
13. `POST /cv/{cv_id}/confirm` — Xác nhận và lưu dữ liệu CV vào hồ sơ cá nhân
14. `GET /evaluation/me` — Xem báo cáo đánh giá năng lực AI và tóm tắt LLM
15. `POST /jobs` — Tạo tin tuyển dụng mới
16. `GET /jobs` — Xem danh sách tin tuyển dụng của NTD
17. `GET /jobs/{job_id}` — Xem chi tiết 1 tin tuyển dụng
18. `PUT /jobs/{job_id}` — Cập nhật tiêu đề, mô tả, số năm kinh nghiệm của JD
19. `DELETE /jobs/{job_id}` — Xóa tin tuyển dụng và liên kết kỹ năng
20. `PATCH /jobs/{job_id}/status` — Đóng / Mở lại tin tuyển dụng
21. `POST /jobs/{job_id}/skills` — Gắn kỹ năng bắt buộc / ưu tiên vào JD
22. `DELETE /jobs/{job_id}/skills/{skill_id}` — Gỡ kỹ năng khỏi JD
23. `GET /candidates` — Tìm kiếm và lọc ứng viên công khai (đa kỹ năng, cấp độ)
24. `GET /jobs/{job_id}/matches` — Xếp hạng đối sánh ứng viên theo JD

---

### 4. MINH CHỨNG TỰ ĐỘNG HÓA
Bộ kịch bản kiểm thử End-to-End và Phân quyền đã được tự động hóa hoàn toàn trong:
* `backend/tests/test_kt04_e2e_integration.py` — Đạt **100% PASS** trong **1.98 giây**.
