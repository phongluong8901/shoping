import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

def ensure_db_exists_postgres():
    # 1. Kết nối đến database mặc định là 'postgres' để có quyền tạo DB mới
    conn = psycopg2.connect(
        dbname='postgres', 
        user='postgres', 
        password='Condien123@', 
        host='localhost'
    )
    
    # 2. Bắt buộc phải bật autocommit để chạy lệnh CREATE DATABASE
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    
    cur = conn.cursor()
    
    # 3. Kiểm tra xem database đã tồn tại chưa
    cur.execute("SELECT 1 FROM pg_catalog.pg_database WHERE datname = 'shopping_db'")
    exists = cur.fetchone()
    
    if not exists:
        print(">>> Đang tạo database shopping_db...", flush=True)
        cur.execute('CREATE DATABASE shopping_db')
    else:
        print(">>> Database shopping_db đã tồn tại.", flush=True)
        
    cur.close()
    conn.close()

# Gọi hàm này trước khi khởi tạo SQLAlchemy Engine
ensure_db_exists_postgres()