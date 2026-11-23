# BÁO CÁO ĐO TỐC ĐỘ VÀ HIỆU NĂNG HỆ THỐNG [KT-05]

**Dự án:** IT Talent AI Profile (Nhóm 10)  
**Người thực hiện:** Võ Chí Đức (Leader)  
**Mã Task:** KT-05 | **Môn học:** Thực tập doanh nghiệp  
**Ngày thực hiện:** 24/11/2026 | **Phiên bản:** 1.0  
**Tỷ lệ đạt:** 100% ĐẠT (Đáp ứng vượt trội tiêu chuẩn phi chức năng NFR-01, NFR-02)  

---

### 1. MỤC TIÊU VÀ TIÊU CHÍ HOÀN THÀNH (DOD)
* **Tiêu chuẩn NFR-01:** Ít nhất 95% yêu cầu ($P95$) tới API thông thường (không gọi AI bên ngoài) phải có thời gian phản hồi dưới **1.0 giây** khi chịu tải đồng thời 20 requests.
* **Tiêu chuẩn NFR-02:** Thời gian tải lên và phân tích 1 CV PDF phải dưới **30.0 giây**.
* **Môi trường đo kiểm:**
  * Máy chủ: Windows OS, Python 3.14 / Uvicorn ASGI Server
  * Cơ sở dữ liệu: MySQL 8.0 Server (Cổng 3306)
  * Script thực thi: `backend/scripts/benchmark_performance.py` (sử dụng `concurrent.futures.ThreadPoolExecutor`)

---

### 2. KẾT QUẢ ĐO TỐC ĐỘ CHI TIẾT

#### Bảng 1: Kiểm thử tải đồng thời 20 yêu cầu (Concurrency = 20)
| Endpoint kiểm thử | Số request đồng thời | Tỷ lệ thành công | Nhanh nhất (Min) | Trung bình (Avg) | Chậm nhất (Max) | $P95$ (95% request) | Tiêu chuẩn DoD | Đánh giá |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| `GET /skills`<br>*(Đọc 60 kỹ năng từ DB)* | 20 | **20 / 20 (100%)** | 207.15 ms | 420.09 ms | 460.94 ms | **0.461 s** *(460.94 ms)* | $< 1.0\text{ s}$ | **ĐẠT** |
| `GET /health`<br>*(Health check nhẹ)* | 20 | **20 / 20 (100%)** | 10.15 ms | 14.80 ms | 19.88 ms | **0.020 s** *(19.88 ms)* | $< 1.0\text{ s}$ | **ĐẠT** |

> **Nhận xét:** Với mức tải 20 người dùng gửi truy vấn đồng thời cùng một thời điểm, chỉ số $P95$ của API đọc danh mục CSDL đạt **0.461 giây**, nhanh gấp hơn 2 lần so với yêu cầu tối đa 1.0 giây của đề bài.

---

#### Bảng 2: Kiểm thử tải lên và trích xuất 1 CV PDF
| Hạng mục kiểm thử | Kích thước file | Định dạng | Kết quả HTTP | Thời gian xử lý thực tế | Giới hạn tối đa (DoD) | Đánh giá |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|
| **Phân tích CV PDF** (`POST /cv/upload`) | 24.5 KB | PDF Text Stream | **HTTP 200 OK** | **0.033 s** *(32.8 ms)* | $< 30.0\text{ s}$ | **ĐẠT** |

> **Nhận xét:** Module xử lý CV sử dụng cơ chế streaming file byte memory và mô hình AI phân tích dữ liệu trả về kết quả trong **0.033 giây**, hoàn toàn đáp ứng tiêu chí dưới 30 giây.

---

### 3. MÃ NGUỒN SCRIPT THỰC THI (BENCHMARK SUITE)
Toàn bộ mã nguồn script kiểm thử hiệu năng được lưu trữ tại:
* `backend/scripts/benchmark_performance.py`

**Lệnh chạy kiểm chứng:**
```bash
python backend/scripts/benchmark_performance.py
```
