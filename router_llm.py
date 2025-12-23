from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import os

router = APIRouter()

class ChatRequest(BaseModel):
    message: str
    context_data: list = [] # Gửi kèm danh sách chi tiêu để AI phân tích

@router.post("/chat")
async def chat_with_ai(request: ChatRequest):
    try:
        # Giả lập logic AI (Bạn có thể thay bằng gọi OpenAI/Gemini tại đây)
        user_msg = request.message
        count = len(request.context_data)
        
        reply = f"AI phản hồi: Tôi đã nhận được thông điệp '{user_msg}'. "
        if count > 0:
            reply += f"Tôi thấy bạn đang có {count} khoản chi tiêu trong danh sách."
        
        return {"reply": reply}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))