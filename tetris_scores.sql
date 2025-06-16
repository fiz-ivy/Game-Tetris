-- Tạo database
CREATE DATABASE IF NOT EXISTS tetris_scores;
USE tetris_scores;

-- Tạo bảng lưu điểm
CREATE TABLE IF NOT EXISTS scores (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(255),
  score INT
); 