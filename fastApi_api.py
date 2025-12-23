import os
import urllib.parse
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import router_llm

# --- 1. CẤU HÌNH KẾT NỐI ---
# Nếu chạy trên Render, lấy URL từ biến môi trường "DATABASE_URL"
# Nếu chạy ở máy (localhost), dùng thông tin của bạn
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    # Thông tin chạy dưới localhost (Nếu bạn cài Postgres máy cá nhân)
    DB_USER = "postgres"
    DB_PASS = urllib.parse.quote_plus("Condien123@")
    DB_HOST = "localhost"
    db_host_env = os.getenv("DB_HOST", "localhost")
    DB_PORT = "5432"
    DB_NAME = "shopping_db"
    DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASS}@{db_host_env}:{DB_PORT}/{DB_NAME}"

# Render thường trả về URL bắt đầu bằng postgres://, 
# nhưng SQLAlchemy yêu cầu postgresql:// (có thêm 'ql')
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# --- 2. CẤU HÌNH SQLALCHEMY ---
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# --- 3. ĐỊNH NGHĨA MODEL ---
class ShoppingItemModel(Base):
    __tablename__ = "history"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False) # Postgres không bắt buộc độ dài String
    price = Column(Float, nullable=False)

# Tạo bảng tự động trong Postgres
Base.metadata.create_all(bind=engine)

# Khởi tạo dữ liệu mẫu nếu bảng trống
def init_sample_data():
    db = SessionLocal()
    try:
        if db.query(ShoppingItemModel).count() == 0:
            print(">>> DB Trống! Đang nạp dữ liệu mẫu vào Postgres...", flush=True)
            samples = [
                ShoppingItemModel(name="Cơm trưa", price=35000),
                ShoppingItemModel(name="Xăng xe", price=50000)
            ]
            db.add_all(samples)
            db.commit()
    finally:
        db.close()

init_sample_data()

# --- 4. FASTAPI SETUP ---
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,        # THÊM DÒNG NÀY: Cho phép gửi kèm headers/cookies (danh cho ngrok)
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

class ShoppingItemSchema(BaseModel):
    name: str
    price: float

# Đăng ký router
app.include_router(router_llm.router, prefix="/ai", tags=["LLM"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- 5. ENDPOINTS ---
@app.get("/history")
def get_history(db: Session = Depends(get_db)):
    items = db.query(ShoppingItemModel).all()
    total = sum(item.price for item in items)
    history_data = [{"name": item.name, "price": item.price} for item in items]
    
    print(f"total: {total}", flush=True)
    print(f"db_shopping: {history_data}", flush=True)
    return {"history": history_data, "total": total}

@app.post("/add-item")
def add_item(item: ShoppingItemSchema, db: Session = Depends(get_db)):
    print(f"item_before: {item}", flush=True)
    new_item = ShoppingItemModel(name=item.name, price=item.price)
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    print(f"item_after: {new_item.name}", flush=True)
    return {"status": "success", "message": f"Đã thêm {new_item.name} vào Postgres"}

if __name__ == "__main__":
    import uvicorn
    # Render sẽ tự gán port qua biến môi trường, mặc định là 10000
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)