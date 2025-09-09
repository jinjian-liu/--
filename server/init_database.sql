-- MySQL数据库初始化脚本
-- 用于创建NLP客户问题反馈分析与管理系统所需的数据库和表结构

-- 设置会话字符集
SET NAMES utf8mb4;

-- 创建数据库
CREATE DATABASE IF NOT EXISTS nlp_feedback CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 切换到创建的数据库
USE nlp_feedback;

-- 再次确认字符集设置
SET character_set_client = utf8mb4;
SET character_set_connection = utf8mb4;
SET character_set_results = utf8mb4;

-- 创建问题表（先创建被引用的表）
CREATE TABLE IF NOT EXISTS problems (
    id INT PRIMARY KEY AUTO_INCREMENT,
    summary VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    type VARCHAR(50) NOT NULL,
    severity VARCHAR(20) NOT NULL,
    feedback_count INT NOT NULL DEFAULT 1,
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    create_time DATETIME NOT NULL,
    update_time DATETIME NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 创建反馈表
CREATE TABLE IF NOT EXISTS feedbacks (
    id INT PRIMARY KEY AUTO_INCREMENT,
    content TEXT NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    problem_id INT,
    create_time DATETIME NOT NULL,
    update_time DATETIME NOT NULL,
    FOREIGN KEY (problem_id) REFERENCES problems(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 创建反馈示例表
CREATE TABLE IF NOT EXISTS feedback_examples (
    id INT PRIMARY KEY AUTO_INCREMENT,
    problem_id INT NOT NULL,
    content TEXT NOT NULL,
    create_time DATETIME NOT NULL,
    FOREIGN KEY (problem_id) REFERENCES problems(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 创建分析结果表
CREATE TABLE IF NOT EXISTS analysis_results (
    id INT PRIMARY KEY AUTO_INCREMENT,
    analysis_type VARCHAR(50) NOT NULL,
    content TEXT NOT NULL,
    start_date DATE,
    end_date DATE,
    create_time DATETIME NOT NULL,
    update_time DATETIME NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 插入一些示例数据
INSERT INTO problems (summary, description, type, severity, feedback_count, status, create_time, update_time)
VALUES (
    '系统登录困难',
    '用户反馈系统登录页面加载缓慢，经常出现验证码错误或无法登录的情况',
    '技术问题',
    '高',
    5,
    'pending',
    NOW(),
    NOW()
);

INSERT INTO feedback_examples (problem_id, content, create_time)
VALUES (
    LAST_INSERT_ID(),
    '我已经尝试了好几次登录系统，但每次都提示验证码错误，即使我输入的是正确的',
    NOW()
);

-- 由于database.py中会自动初始化数据，这里不再手动插入示例数据
-- INSERT INTO feedbacks (content, status, problem_id, create_time, update_time)
-- VALUES (
--     '我已经尝试了好几次登录系统，但每次都提示验证码错误，即使我输入的是正确的',
--     'pending',
--     1, -- 明确引用第一个problems记录
--     NOW(),
--     NOW()
-- );

-- 创建索引以提高查询性能
CREATE INDEX idx_feedback_status ON feedbacks(status);
CREATE INDEX idx_feedback_problem_id ON feedbacks(problem_id);
CREATE INDEX idx_problems_status ON problems(status);
CREATE INDEX idx_problems_type ON problems(type);

-- 显示创建的数据库和表信息
SELECT '数据库初始化完成' AS message;
SHOW TABLES;