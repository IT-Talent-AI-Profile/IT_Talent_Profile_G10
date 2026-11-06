-- =====================================================================
-- HỆ THỐNG IT TALENT AI PROFILE (NHÓM 10)
-- Script: database/sample_data.sql (Task [NT-04] - Phụ trách: Đức)
-- Mục đích: Dữ liệu mẫu phục vụ kiểm thử:
-- - 2 tài khoản NTD và 6 tài khoản ứng viên (4 công khai, 2 riêng tư)
-- - Mỗi hồ sơ có 3-6 kỹ năng, đủ 4 cấp độ Intern/Junior/Middle/Senior
-- - 3 JD (2 mở, 1 đóng) với kỹ năng bắt buộc và ưu tiên
-- Mật khẩu chung của tất cả tài khoản: 12345678 (đã băm bằng bcrypt)
-- =====================================================================

USE it_talent_ai;

-- 1. TẠO 8 TÀI KHOẢN MẪU (2 NTD, 6 ỨNG VIÊN)
-- Chuỗi băm bcrypt của mật khẩu '12345678': $2b$12$qnxkq/P3jMhS5cBrgCW3m.7xQirGLeNq9kjWgN4./9sRPc8wUnjTG
INSERT INTO users (id, email, password_hash, role) VALUES
(1, 'hr.techcorp@example.com', '$2b$12$qnxkq/P3jMhS5cBrgCW3m.7xQirGLeNq9kjWgN4./9sRPc8wUnjTG', 'recruiter'),
(2, 'talent.innovate@example.com', '$2b$12$qnxkq/P3jMhS5cBrgCW3m.7xQirGLeNq9kjWgN4./9sRPc8wUnjTG', 'recruiter'),
(3, 'nguyen.senior@example.com', '$2b$12$qnxkq/P3jMhS5cBrgCW3m.7xQirGLeNq9kjWgN4./9sRPc8wUnjTG', 'candidate'),
(4, 'tran.middle@example.com', '$2b$12$qnxkq/P3jMhS5cBrgCW3m.7xQirGLeNq9kjWgN4./9sRPc8wUnjTG', 'candidate'),
(5, 'le.junior@example.com', '$2b$12$qnxkq/P3jMhS5cBrgCW3m.7xQirGLeNq9kjWgN4./9sRPc8wUnjTG', 'candidate'),
(6, 'pham.intern@example.com', '$2b$12$qnxkq/P3jMhS5cBrgCW3m.7xQirGLeNq9kjWgN4./9sRPc8wUnjTG', 'candidate'),
(7, 'hoang.private_senior@example.com', '$2b$12$qnxkq/P3jMhS5cBrgCW3m.7xQirGLeNq9kjWgN4./9sRPc8wUnjTG', 'candidate'),
(8, 'vu.private_junior@example.com', '$2b$12$qnxkq/P3jMhS5cBrgCW3m.7xQirGLeNq9kjWgN4./9sRPc8wUnjTG', 'candidate')
ON DUPLICATE KEY UPDATE email = VALUES(email);

-- 2. TẠO 6 HỒ SƠ ỨNG VIÊN (4 CÔNG KHAI, 2 RIÊNG TƯ, ĐỦ 4 CẤP ĐỘ)
INSERT INTO profiles (id, user_id, full_name, desired_position, years_experience, education, experience, github_url, is_public, level, total_score, ai_summary) VALUES
(1, 3, 'Nguyễn Văn Senior', 'Senior Backend Engineer', 6.0, 'Đại học Bách Khoa, CNTT', '6 năm phát triển hệ thống backend phân tán với Python, MySQL, Docker', 'https://github.com/nguyensenior', 1, 'Senior', 85.0, 'Lập trình viên backend giàu kinh nghiệm, chuyên sâu về Python, kiến trúc phân tán và tối ưu CSDL.'),
(2, 4, 'Trần Thị Middle', 'Backend Developer', 3.0, 'Đại học Khoa học Tự nhiên', '3 năm lập trình API backend với Python và cơ sở dữ liệu quan hệ', 'https://github.com/tranmiddle', 1, 'Middle', 68.0, 'Kỹ sư phần mềm vững nền tảng RESTful API và quản trị cơ sở dữ liệu quan hệ.'),
(3, 5, 'Lê Văn Junior', 'Frontend Developer', 1.5, 'Đại học Công nghệ - ĐHQG', '1.5 năm phát triển giao diện người dùng với React, JavaScript', 'https://github.com/lejunior', 1, 'Junior', 48.0, 'Lập trình viên frontend trẻ, nhiệt huyết, nắm vững React, responsive web và UI/UX cơ bản.'),
(4, 6, 'Phạm Quốc Intern', 'Fresher / Intern Python', 0.5, 'Đại học FPT', 'Thực tập sinh Python, hoàn thành các dự án đồ án môn học', 'https://github.com/phamintern', 1, 'Intern', 30.0, 'Sinh viên mới tốt nghiệp, nắm chắc cú pháp Python và kiến thức cơ bản về CSDL.'),
(5, 7, 'Hoàng Private Senior', 'Lead Cloud Architect', 5.5, 'Đại học Bách Khoa', '5.5 năm làm DevOps, AWS, Docker và Microservices', 'https://github.com/hoangprivate', 0, 'Senior', 88.0, 'Chuyên gia điện toán đám mây và hạ tầng CI/CD, hồ sơ đang đặt ở chế độ riêng tư.'),
(6, 8, 'Vũ Private Junior', 'Junior Java Developer', 1.0, 'Đại học Công nghiệp', '1 năm lập trình Java Spring Boot', 'https://github.com/vuprivate', 0, 'Junior', 42.0, 'Lập trình viên Java Junior, hồ sơ riêng tư.')
ON DUPLICATE KEY UPDATE full_name = VALUES(full_name);

-- 3. GẮN KỸ NĂNG CHO TỪNG HỒ SƠ (3 - 5 KỸ NĂNG MỖI HỒ SƠ)
INSERT INTO profile_skills (profile_id, skill_id, proficiency, years_used) VALUES
-- Hồ sơ 1 (Senior Backend: Python=1, MySQL=21, Docker=31, RESTful API=51, System Design=56)
(1, 1, 5, 6.0),
(1, 21, 4, 5.0),
(1, 31, 4, 4.0),
(1, 51, 5, 5.0),
(1, 56, 4, 3.0),

-- Hồ sơ 2 (Middle Backend: Python=1, RESTful API=51, PostgreSQL=22, Git=34)
(2, 1, 4, 3.0),
(2, 51, 4, 3.0),
(2, 22, 3, 2.0),
(2, 34, 4, 3.0),

-- Hồ sơ 3 (Junior Frontend: React=15, JavaScript=13, HTML=11, CSS=12)
(3, 15, 3, 1.5),
(3, 13, 3, 1.5),
(3, 11, 4, 2.0),
(3, 12, 4, 2.0),

-- Hồ sơ 4 (Intern: Python=1 (prof=2), Git=34 (prof=2), MySQL=21 (prof=2))
(4, 1, 2, 0.5),
(4, 34, 2, 0.5),
(4, 21, 2, 0.5),

-- Hồ sơ 5 (Private Senior: Python=1, AWS=37, Docker=31, Microservices=53)
(5, 1, 5, 5.5),
(5, 37, 5, 4.0),
(5, 31, 5, 5.0),
(5, 53, 4, 4.0),

-- Hồ sơ 6 (Private Junior: Java=2, MySQL=21, OOP=57)
(6, 2, 3, 1.0),
(6, 21, 3, 1.0),
(6, 57, 3, 1.0)
ON DUPLICATE KEY UPDATE proficiency = VALUES(proficiency);

-- 4. TẠO 3 JD (2 MỞ, 1 ĐÓNG)
INSERT INTO jobs (id, recruiter_id, title, description, min_years, is_open) VALUES
(1, 1, 'Senior Python Backend Engineer', 'Tuyển Senior Python tham gia xây dựng hệ thống phân tán, chịu tải cao.', 5.0, 1),
(2, 1, 'Junior Frontend React Developer', 'Tuyển dụng Junior Frontend thành thạo React và JavaScript để phát triển giao diện.', 1.0, 1),
(3, 2, 'DevOps Engineer (Đã đủ chỉ tiêu)', 'Tuyển kỹ sư vận hành hệ thống CI/CD và Kubernetes.', 3.0, 0)
ON DUPLICATE KEY UPDATE title = VALUES(title);

-- 5. GẮN KỸ NĂNG CHO JD (KỸ NĂNG BẮT BUỘC = 1, ƯU TIÊN = 0)
INSERT INTO job_skills (job_id, skill_id, is_required) VALUES
-- JD 1 (Senior Python): Bắt buộc: Python(1), MySQL(21); Ưu tiên: Docker(31), System Design(56)
(1, 1, 1),
(1, 21, 1),
(1, 31, 0),
(1, 56, 0),

-- JD 2 (Junior React): Bắt buộc: React(15), JavaScript(13); Ưu tiên: Tailwind CSS(19)
(2, 15, 1),
(2, 13, 1),
(2, 19, 0),

-- JD 3 (DevOps - Đã đóng): Bắt buộc: Docker(31), Kubernetes(32); Ưu tiên: AWS(37)
(3, 31, 1),
(3, 32, 1),
(3, 37, 0)
ON DUPLICATE KEY UPDATE is_required = VALUES(is_required);
