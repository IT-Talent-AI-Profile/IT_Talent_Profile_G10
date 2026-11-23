"""
Benchmark Script for KT-05: Đo tốc độ hệ thống IT Talent AI Profile
- Gửi 20 requests đồng thời vào API thường (/skills và /health).
- Đo thời gian phản hồi min, max, trung bình, P95.
- Đo thời gian phân tích 1 CV PDF.
"""
import time
import concurrent.futures
import statistics
import requests
import io
from pypdf import PdfWriter

BASE_URL = "http://127.0.0.1:8000"


def generate_sample_pdf() -> bytes:
    writer = PdfWriter()
    writer.add_blank_page(width=72, height=72)
    stream = io.BytesIO()
    writer.write(stream)
    return stream.getvalue()


def send_get_request(url: str, headers: dict = None):
    start = time.perf_counter()
    res = requests.get(url, headers=headers or {}, timeout=10)
    elapsed = time.perf_counter() - start
    return res.status_code, elapsed


def benchmark_concurrent_api(url: str, n_requests: int = 20, headers: dict = None):
    print(f"\n[1] Bắt đầu benchmark {n_requests} requests đồng thời tới {url}...")
    times = []
    statuses = []

    start_total = time.perf_counter()
    with concurrent.futures.ThreadPoolExecutor(max_workers=n_requests) as executor:
        futures = [executor.submit(send_get_request, url, headers) for _ in range(n_requests)]
        for future in concurrent.futures.as_completed(futures):
            status, duration = future.result()
            times.append(duration)
            statuses.append(status)
    total_duration = time.perf_counter() - start_total

    times_sorted = sorted(times)
    p95_idx = int(len(times_sorted) * 0.95)
    p95_val = times_sorted[min(p95_idx, len(times_sorted) - 1)]

    result = {
        "url": url,
        "n_requests": n_requests,
        "success_count": statuses.count(200),
        "total_duration_sec": total_duration,
        "min_sec": min(times),
        "max_sec": max(times),
        "avg_sec": statistics.mean(times),
        "p95_sec": p95_val,
    }
    return result


def benchmark_cv_upload():
    print("\n[2] Bắt đầu benchmark phân tích 1 CV PDF...")
    # Đăng nhập lấy token
    login_res = requests.post(
        f"{BASE_URL}/auth/login",
        json={"email": "nguyen.senior@example.com", "password": "12345678"},
        timeout=10
    )
    if login_res.status_code != 200:
        print("Lỗi đăng nhập:", login_res.text)
        return None

    token = login_res.json()["token"]
    headers = {"Authorization": f"Bearer {token}"}

    pdf_bytes = generate_sample_pdf()
    files = {"file": ("benchmark_cv.pdf", pdf_bytes, "application/pdf")}

    start = time.perf_counter()
    res = requests.post(f"{BASE_URL}/cv/upload", headers=headers, files=files, timeout=30)
    duration = time.perf_counter() - start

    return {
        "status_code": res.status_code,
        "duration_sec": duration,
        "response": res.json() if res.status_code == 200 else res.text
    }


if __name__ == "__main__":
    print("==================================================")
    print("  CHẠY BENCHMARK ĐO TỐC ĐỘ HỆ THỐNG (TASK KT-05)  ")
    print("==================================================")

    # Lấy token xác thực
    login_res = requests.post(
        f"{BASE_URL}/auth/login",
        json={"email": "nguyen.senior@example.com", "password": "12345678"},
        timeout=10
    )
    token = login_res.json()["token"] if login_res.status_code == 200 else ""
    auth_headers = {"Authorization": f"Bearer {token}"} if token else {}

    # 1. Đo 20 requests đồng thời tới /skills (API danh mục kỹ năng chuẩn có xác thực)
    res_skills = benchmark_concurrent_api(f"{BASE_URL}/skills", 20, headers=auth_headers)
    print(f"-> Kết quả /skills:")
    print(f"   Thành công (HTTP 200):      {res_skills['success_count']}/{res_skills['n_requests']}")
    print(f"   Thời gian nhanh nhất (Min): {res_skills['min_sec']*1000:.2f} ms")
    print(f"   Thời gian trung bình (Avg): {res_skills['avg_sec']*1000:.2f} ms")
    print(f"   P95 (95% requests):         {res_skills['p95_sec']*1000:.2f} ms ({res_skills['p95_sec']:.3f} s)")
    print(f"   Thời gian chậm nhất (Max):  {res_skills['max_sec']*1000:.2f} ms")
    print(f"   Đạt tiêu chuẩn < 1 giây:    {'ĐẠT' if res_skills['p95_sec'] < 1.0 else 'KHÔNG ĐẠT'}")

    # 2. Đo 20 requests đồng thời tới /health
    res_health = benchmark_concurrent_api(f"{BASE_URL}/health", 20)
    print(f"\n-> Kết quả /health:")
    print(f"   Thành công: {res_health['success_count']}/{res_health['n_requests']}")
    print(f"   P95:                        {res_health['p95_sec']*1000:.2f} ms ({res_health['p95_sec']:.3f} s)")
    print(f"   Đạt tiêu chuẩn < 1 giây:    {'ĐẠT' if res_health['p95_sec'] < 1.0 else 'KHÔNG ĐẠT'}")

    # 3. Đo phân tích 1 CV
    res_cv = benchmark_cv_upload()
    if res_cv:
        print(f"\n-> Kết quả tải và phân tích 1 CV:")
        print(f"   HTTP Status:                {res_cv['status_code']}")
        print(f"   Thời gian xử lý:            {res_cv['duration_sec']:.3f} s ({res_cv['duration_sec']*1000:.2f} ms)")
        print(f"   Đạt tiêu chuẩn < 30 giây:   {'ĐẠT' if res_cv['duration_sec'] < 30.0 else 'KHÔNG ĐẠT'}")
