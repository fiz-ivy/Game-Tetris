# Tetris Game

Một dự án game Tetris viết bằng Python sử dụng Pygame, có lưu điểm số vào MySQL

## Tính năng
- Chơi Tetris với hình nền động
- Lưu điểm số vào MySQL
- Bảng xếp hạng top 10
- Giao diện đẹp, dễ sử dụng

## Yêu cầu hệ thống
- Python 3.8+
- MySQL Server
- Các thư viện Python: pygame, mysql-connector-python

## Cài đặt
1. Cài Python và pip nếu chưa có.
2. Cài các thư viện cần thiết:
   ```bash
   pip install -r requirements.txt
   ```
3. Cài đặt MySQL, tạo database và bảng:
   ```sql
   CREATE DATABASE tetris_scores;
   USE tetris_scores;
   CREATE TABLE scores (
     id INT AUTO_INCREMENT PRIMARY KEY,
     name VARCHAR(255),
     score INT
   );
   ```
4. Đảm bảo các file ảnh (1.jpg, 2.jpg, 3.jpg, 4.jpg, 5.jpg, 6.jpg, 7.jpg) nằm cùng thư mục với mã nguồn.

## Chạy game
```bash
python demoj.py
```