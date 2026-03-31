from fastapi import FastAPI, Request
import uvicorn
import os
from dotenv import load_dotenv
from httplib2 import Http
from json import dumps
from fastapi.responses import JSONResponse

# Import hàm từ thư mục src
from src.rag_engine import ask_vitex

load_dotenv()

app = FastAPI(title="Vitex RAG Bot")

@app.get("/")
async def health_check():
    return {"status": "Vitex Bot is Online", "model": "Gemini 3 Flash"}

@app.post("/webhook")
async def google_chat_webhook(request: Request):
    event = await request.json()
    
    # 1. Kiểm tra tin nhắn
    chat_data = event.get("chat", {})
    message_payload = chat_data.get("messagePayload", {})
    message_obj = message_payload.get("message", {})
    
    # Lấy nội dung tin nhắn
    user_text = message_obj.get("text")
    
    if user_text:
        try:
            # 2. Gọi RAG
            # answer = ask_vitex(user_text)
            
            # 3. Trả về format Google Chat
            #chatbot(user_text)
            return create_action_response(ask_vitex(user_text))
        except Exception as e:
            print(f"Lỗi RAG: {e}")
            #chatbot(f"Phản hồi lại : Bot gặp lỗi khi xử lý AI: {str(e)}")#{"text": f"Bot gặp lỗi khi xử lý AI: {str(e)}"}
            return create_action_response(f"Bot gặp lỗi khi xử lý AI: {str(e)}")

    # 4. Trường hợp không phải tin nhắn
    print("Không phải tin nhắn")
    #chatbot("Phản hồi lại : Bot Vitex đã nhận tín hiệu nhưng không thấy nội dung tin nhắn.")#{"text": "Bot Vitex đã nhận tín hiệu nhưng không thấy nội dung tin nhắn."}
    return create_action_response("Bot Vitex đã nhận tín hiệu nhưng không thấy nội dung tin nhắn.")

# def chatbot(user_text):
#     """Google Chat incoming webhook quickstart."""
#     url = "https://chat.googleapis.com/v1/spaces/AAQAawP_lqA/messages?key=AIzaSyDdI0hCZtE6vySjMm-WEfRq3CPzqKqqsHI&token=dEhg1ilSX5AxA4W4vcHpx30XH_aWRjGQ6QgJzQ5jUMY"
#     app_message = {
#         "text": ask_vitex(user_text)
#     }
#     message_headers = {"Content-Type": "application/json; charset=UTF-8"}
#     http_obj = Http()
#     response = http_obj.request(
#         uri=url,
#         method="POST",
#         headers=message_headers,
#         body=dumps(app_message),
#     )
#     print(response)

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
    uvicorn.run("test_demo:app", host="0.0.0.0", port=8000, reload=True)