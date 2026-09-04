CREATE DATABASE IF NOT EXISTS code_evaluator;
USE code_evaluator;

CREATE TABLE IF NOT EXISTS submissions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    language VARCHAR(50) NOT NULL,
    code TEXT NOT NULL,
    status VARCHAR(50) NOT NULL,
    output TEXT,
    execution_time_ms INT,
    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);