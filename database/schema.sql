-- =====================================================================
-- HỆ THỐNG IT TALENT AI PROFILE (NHÓM 10)
-- Script: database/schema.sql
-- Mục đích: Khởi tạo database và 7 bảng nghiệp vụ theo tài liệu Thiết kế hệ thống (Mục 5.3, 5.4, 5.5)
-- =====================================================================

CREATE DATABASE IF NOT EXISTS it_talent_ai
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE it_talent_ai;

-- 1. BẢNG users: Quản lý tài khoản và vai trò
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL COMMENT 'candidate hoặc recruiter',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 2. BẢNG profiles: Hồ sơ năng lực của ứng viên (Quan hệ 1-1 với users)
CREATE TABLE IF NOT EXISTS profiles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL UNIQUE,
    full_name VARCHAR(100) NOT NULL,
    desired_position VARCHAR(100),
    years_experience FLOAT DEFAULT 0,
    education TEXT,
    experience TEXT,
    github_url VARCHAR(255),
    is_public TINYINT(1) DEFAULT 0 COMMENT '1: công khai, 0: riêng tư',
    level VARCHAR(20) COMMENT 'Intern, Junior, Middle, Senior',
    total_score FLOAT COMMENT 'Điểm tổng 0 - 100',
    ai_summary TEXT COMMENT 'Bản tóm tắt do AI sinh',
    CONSTRAINT fk_profiles_user
        FOREIGN KEY (user_id) REFERENCES users(id)
        ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 3. BẢNG skills: Danh mục kỹ năng chuẩn
CREATE TABLE IF NOT EXISTS skills (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    skill_group VARCHAR(50) NOT NULL COMMENT 'Backend, Frontend, Database, DevOps, Data/AI, Khác'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 4. BẢNG profile_skills: Kỹ năng của ứng viên (Quan hệ N-N giữa profiles và skills)
CREATE TABLE IF NOT EXISTS profile_skills (
    id INT AUTO_INCREMENT PRIMARY KEY,
    profile_id INT NOT NULL,
    skill_id INT NOT NULL,
    proficiency TINYINT NOT NULL COMMENT 'Mức thành thạo từ 1 đến 5',
    years_used FLOAT DEFAULT 0 COMMENT 'Số năm sử dụng',
    CONSTRAINT uq_profile_skill UNIQUE (profile_id, skill_id),
    CONSTRAINT fk_profile_skills_profile
        FOREIGN KEY (profile_id) REFERENCES profiles(id)
        ON DELETE CASCADE,
    CONSTRAINT fk_profile_skills_skill
        FOREIGN KEY (skill_id) REFERENCES skills(id)
        ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 5. BẢNG cv_files: File CV ứng viên tải lên và kết quả phân tích của AI
CREATE TABLE IF NOT EXISTS cv_files (
    id INT AUTO_INCREMENT PRIMARY KEY,
    profile_id INT NOT NULL,
    file_name VARCHAR(255) NOT NULL COMMENT 'Tên gốc file tải lên',
    file_path VARCHAR(500) NOT NULL COMMENT 'Đường dẫn file lưu trữ trên server',
    file_size INT COMMENT 'Kích thước file (byte), tối đa 5MB (5242880)',
    status VARCHAR(20) NOT NULL COMMENT 'pending, success, failed, confirmed',
    ai_result JSON COMMENT 'Kết quả JSON do LLM trích xuất',
    error_message TEXT COMMENT 'Thông báo lỗi nếu quá trình AI thất bại',
    uploaded_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_cv_files_profile
        FOREIGN KEY (profile_id) REFERENCES profiles(id)
        ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 6. BẢNG jobs: Mô tả công việc (JD) do Nhà tuyển dụng đăng
CREATE TABLE IF NOT EXISTS jobs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    recruiter_id INT NOT NULL,
    title VARCHAR(150) NOT NULL,
    description TEXT,
    min_years FLOAT DEFAULT 0 COMMENT 'Số năm kinh nghiệm tối thiểu',
    is_open TINYINT(1) DEFAULT 1 COMMENT '1: đang mở, 0: đã đóng',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_jobs_recruiter
        FOREIGN KEY (recruiter_id) REFERENCES users(id)
        ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 7. BẢNG job_skills: Kỹ năng của JD (Quan hệ N-N giữa jobs và skills)
CREATE TABLE IF NOT EXISTS job_skills (
    id INT AUTO_INCREMENT PRIMARY KEY,
    job_id INT NOT NULL,
    skill_id INT NOT NULL,
    is_required TINYINT(1) NOT NULL COMMENT '1: bắt buộc, 0: ưu tiên',
    CONSTRAINT uq_job_skill UNIQUE (job_id, skill_id),
    CONSTRAINT fk_job_skills_job
        FOREIGN KEY (job_id) REFERENCES jobs(id)
        ON DELETE CASCADE,
    CONSTRAINT fk_job_skills_skill
        FOREIGN KEY (skill_id) REFERENCES skills(id)
        ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =====================================================================
-- BỔ SUNG 3 CHỈ MỤC (INDEX) BẮT BUỘC THEO MỤC 5.4 TÀI LIỆU THIẾT KẾ
-- =====================================================================
CREATE INDEX idx_profiles_public_level ON profiles(is_public, level);
CREATE INDEX idx_profile_skills_skill ON profile_skills(skill_id);
CREATE INDEX idx_job_skills_skill ON job_skills(skill_id);
