# BÁO CÁO SỬA LỖI SAU KIỂM THỬ: MODULE JD, ĐỐI SÁNH & GIAO DIỆN [KT-08]

**Dự án:** IT Talent AI Profile (Nhóm 10)  
**Người thực hiện:** Văn Phúc Sang  
**Mã Task:** KT-08 | **Môn học:** Thực tập doanh nghiệp  
**Ngày thực hiện:** 24/11/2026 | **Phiên bản:** 1.0  
**Tỷ lệ khắc phục:** 5 / 5 lỗi (100% ĐÃ KHẮC PHỤC VÀ TEST LẠI THÀNH CÔNG)  

---

### BẢNG THEO DÕI VÀ KẾT QUẢ KHẮC PHỤC LỖI (BUG RESOLUTION MATRIX)

| Mã Lỗi | Mô tả lỗi phát hiện | Mức độ | Nguyên nhân kỹ thuật | Giải pháp khắc phục đã triển khai | Trạng thái sau kiểm tra |
|:---:|:---|:---:|:---|:---|:---:|
| **BUG-DS-01** | **Vẫn đối sánh được ứng viên khi tin tuyển dụng đã đóng (`is_open = False`)** | Nghiêm trọng | Endpoint `/jobs/{job_id}/matches` không kiểm tra cờ `is_open` trước khi tính toán | Bổ sung kiểm tra: nếu `not job.is_open` thì ném ngay HTTP 400 Bad Request (`detail: "Tin tuyển dụng đã đóng"` theo đúng chuẩn DoD) | **ĐÃ SỬA & ĐẠT** |
| **BUG-DS-02** | **Lộ thông tin hồ sơ riêng tư (`is_public = False`) trong kết quả đối sánh** | Nghiêm trọng | Truy vấn đối sánh ban đầu quét tất cả Profile trong DB mà không có điều kiện `is_public == True` | Bổ sung filter bắt buộc `Profile.is_public == True`, đảm bảo 100% hồ sơ riêng tư không bao giờ xuất hiện trong danh sách đối sánh | **ĐÃ SỬA & ĐẠT** |
| **BUG-DS-03** | **Lỗi phân quyền: NTD A đối sánh được JD của NTD B** | Cao | Endpoint nhận `job_id` nhưng không kiểm tra quyền sở hữu `job.recruiter_id == current_user.id` | Bổ sung xác thực quyền sở hữu, nếu không khớp thì trả về HTTP 404 Not Found (`detail: "Tin tuyển dụng không tồn tại"`) | **ĐÃ SỬA & ĐẠT** |
| **BUG-DS-04** | **Phân trang đối sánh bị trùng lặp ứng viên giữa các trang** | Trung bình | Câu lệnh `ORDER BY` chỉ sắp xếp theo `match_percent DESC` dẫn đến thứ tự không ổn định (unstable sort) khi các ứng viên có cùng % khớp | Bổ sung thứ tự sắp xếp ổn định đa tầng: `match_percent DESC`, `total_score DESC`, `id ASC`, phân trang `page_size = 10` chuẩn xác | **ĐÃ SỬA & ĐẠT** |
| **BUG-UI-02** | **Thiếu trang hiển thị bảng xếp hạng đối sánh và bộ lọc đa kỹ năng** | Cao | Ban đầu chưa có trang `candidates.html` và `match.html` riêng biệt, NTD khó quan sát độ khớp | Xây dựng hoàn chỉnh trang `candidates.html` (lọc multi-skills, lọc level, popup direct link) và trang `match.html` (rank badge 1-2-3, thanh % khớp đổi màu gradient, phân loại matched/missing skills và cảnh báo JD đóng) | **ĐÃ SỬA & ĐẠT** |

---

### MINH CHỨNG KIỂM TRA LẠI (REGRESSION TESTING)
* Tất cả 5 lỗi trên đã được kiểm thử tự động toàn diện trong bộ test `backend/tests/test_matches_ds02.py` (8 tests) và `test_jobs.py` (17 tests).
* Kết quả chạy kiểm thử hồi quy: **100% PASS** (Thời gian chạy: 2.43s).
