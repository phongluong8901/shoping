import pymysql

# Kết nối tạm vào MySQL (không chỉ định database) để tạo database
connection = pymysql.connect(host='localhost', user='root', password='Condien123@')
try:
    with connection.cursor() as cursor:
        cursor.execute("CREATE DATABASE IF NOT EXISTS shopping_db")
    connection.commit()
finally:
    connection.close()

# Sau đó mới chạy đoạn SQLAlchemy như bình thường
# Base.metadata.create_all(bind=engine)