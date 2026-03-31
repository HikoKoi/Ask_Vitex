from fastapi import FastAPI, Request
import uvicorn
import os
import redis

# Import hàm từ thư mục src
from src.rag_engine import ask_vitex

app = FastAPI(title="Vitex RAG Bot")

r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
# Lưu lại 6 cặp hỏi đáp gần nhất
MAX_HISTORY = 10
# Tự động xóa lịch sử sau 1h không hoạt động
TTL_SECONDS = 60*60

@app.get("/")
async def health_check():
    return {"status": "Vitex Bot is Online", "model": "Gemini 3.1 Flash Lite"}

@app.post("/webhook")
async def google_chat_webhook(request: Request):
    event = await request.json()
    chat_event = event.get("chat", {})
    user_name = (chat_event
                .get("user", {})
                .get("displayName"))
    if "messagePayload" in chat_event:
        msg = (chat_event
                .get("messagePayload", {})
                .get("message", {}))
        user_text = msg.get("argumentText")
        thread_name = msg.get("thread", {}).get("name")
        if user_text:
            try:
                history = r.lrange(thread_name, 0, -1) if thread_name else []
                answer = await ask_vitex(user_text, history)
                if thread_name:
                    r.rpush(thread_name, f"User: {user_text}", f"Bot: {answer}")
                    r.expire(thread_name, TTL_SECONDS)
                    r.ltrim(thread_name, -MAX_HISTORY, -1)
                return create_action_response(answer)
                
            except Exception as e:
                return create_action_response(f"Bot gặp lỗi khi xử lý AI: {str(e)}")

        return create_action_response("Tôi đã nhận được tín hiệu nhưng không thấy nội dung tin nhắn của bạn.")
    
    elif "addedToSpacePayload" in chat_event:
        space_type = (chat_event
                    .get("addedToSpacePayload", {})
                    .get("space", {})
                    .get("type"))
        
        if space_type == "DM":
            return create_action_response(f"""Cảm ơn {user_name} đã thêm tôi vào không gian làm việc Direct Message!
Tôi là Test - trợ lý ảo nội bộ của công ty Vitex, tôi có thể giúp bạn trả lời các câu hỏi liên quan đến quy chế của công ty.
Hãy hỏi tôi bất cứ điều gì bạn muốn!
""")
        elif space_type == "ROOM":
            space_name = (chat_event
                        .get("addedToSpacePayload", {})
                        .get("space", {})
                        .get("displayName"))
            return create_action_response(f"""Cảm ơn {user_name} đã thêm tôi vào không gian làm việc {space_name}!
Tôi là Test - trợ lý ảo nội bộ của công ty Vitex, tôi có thể giúp bạn trả lời các câu hỏi liên quan đến quy chế của công ty.
Hãy @Test tại không gian {space_name} này để hỏi tôi bất cứ điều gì bạn muốn!
""")

def create_action_response(answer):
    return {
        "hostAppDataAction": {
            "chatDataAction": {
                "createMessageAction": {
                    "message": {
                        "text": answer
                    }
                }
            }
        }
    }

if __name__ == "__main__":
    # Chạy server trên port 8000
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)