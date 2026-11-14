import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.api.router import api_router

app = FastAPI(
    title="IT Talent AI Profile API",
    description="Hệ thống đánh giá hồ sơ năng lực IT và đối sánh tuyển dụng thông minh bằng AI",
    version="1.0.0"
)

# Cấu hình CORS cho phép Frontend truy cập
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Nạp router chính tích hợp tất cả các module
app.include_router(api_router)

# Mount thư mục Frontend để chạy web trực tiếp qua http://127.0.0.1:8000/web/
frontend_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "frontend")
if os.path.exists(frontend_dir):
    app.mount("/web", StaticFiles(directory=frontend_dir, html=True), name="web")

@app.get("/", tags=["Hệ thống"])
def root():
    return {
        "message": "IT Talent AI Profile API is running",
        "docs": "/docs",
        "version": "1.0.0"
    }

@app.get("/health", tags=["Hệ thống"])
def health_check():
    return {"status": "ok"}
