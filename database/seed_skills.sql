-- =====================================================================
-- HỆ THỐNG IT TALENT AI PROFILE (NHÓM 10)
-- Script: database/seed_skills.sql
-- Mục đích: Nạp danh mục 60 kỹ năng chuẩn chia đều vào 6 nhóm (10 kỹ năng/nhóm)
-- Các nhóm: Backend, Frontend, Database, DevOps, Data/AI, Khác
-- =====================================================================

USE it_talent_ai;

INSERT INTO skills (name, skill_group) VALUES
-- 1. Nhóm Backend (10 kỹ năng)
('Python', 'Backend'),
('Java', 'Backend'),
('C#', 'Backend'),
('Golang', 'Backend'),
('Node.js', 'Backend'),
('PHP', 'Backend'),
('Ruby', 'Backend'),
('Rust', 'Backend'),
('C++', 'Backend'),
('Kotlin', 'Backend'),

-- 2. Nhóm Frontend (10 kỹ năng)
('HTML', 'Frontend'),
('CSS', 'Frontend'),
('JavaScript', 'Frontend'),
('TypeScript', 'Frontend'),
('React', 'Frontend'),
('Angular', 'Frontend'),
('Vue.js', 'Frontend'),
('Next.js', 'Frontend'),
('Tailwind CSS', 'Frontend'),
('Bootstrap', 'Frontend'),

-- 3. Nhóm Database (10 kỹ năng)
('MySQL', 'Database'),
('PostgreSQL', 'Database'),
('MongoDB', 'Database'),
('Redis', 'Database'),
('Oracle', 'Database'),
('Microsoft SQL Server', 'Database'),
('SQLite', 'Database'),
('Cassandra', 'Database'),
('Elasticsearch', 'Database'),
('Firebase', 'Database'),

-- 4. Nhóm DevOps (10 kỹ năng)
('Docker', 'DevOps'),
('Kubernetes', 'DevOps'),
('CI/CD', 'DevOps'),
('Git', 'DevOps'),
('Linux', 'DevOps'),
('Jenkins', 'DevOps'),
('AWS', 'DevOps'),
('Azure', 'DevOps'),
('Google Cloud', 'DevOps'),
('Terraform', 'DevOps'),

-- 5. Nhóm Data/AI (10 kỹ năng)
('Machine Learning', 'Data/AI'),
('Deep Learning', 'Data/AI'),
('PyTorch', 'Data/AI'),
('TensorFlow', 'Data/AI'),
('Pandas', 'Data/AI'),
('NumPy', 'Data/AI'),
('Scikit-learn', 'Data/AI'),
('Computer Vision', 'Data/AI'),
('NLP', 'Data/AI'),
('Data Analysis', 'Data/AI'),

-- 6. Nhóm Khác (10 kỹ năng)
('RESTful API', 'Khác'),
('GraphQL', 'Khác'),
('Microservices', 'Khác'),
('Agile/Scrum', 'Khác'),
('Unit Testing', 'Khác'),
('System Design', 'Khác'),
('OOP', 'Khác'),
('Web Security', 'Khác'),
('UI/UX Design', 'Khác'),
('Figma', 'Khác')
ON DUPLICATE KEY UPDATE skill_group = VALUES(skill_group);
