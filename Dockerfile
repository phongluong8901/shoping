# Sử dụng Python bản nhẹ
FROM python:3.11-slim

# Đặt thư mục làm việc trong container
WORKDIR /app

# Copy file requirements và cài đặt
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy toàn bộ code vào trong Docker
COPY . .

# Chạy app với Uvicorn
# Render sẽ tự cấp PORT qua biến môi trường, nên dùng $PORT
CMD uvicorn fastApi_api:app --host 0.0.0.0 --port ${PORT:-10000}