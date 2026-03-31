from fastapi import FastAPI, Request
import uvicorn
import os

# Import hàm từ thư mục src
from src.rag_engine import ask_vitex

app = FastAPI(title="Vitex RAG Bot")

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
        user_text = (chat_event
                    .get("messagePayload", {})
                    .get("message", {})
                    .get("argumentText"))
        
        if user_text:
            try:
                answer = await ask_vitex(user_text)
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