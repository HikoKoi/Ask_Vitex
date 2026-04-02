import asyncio
import redis
import httpx
import os
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime
from dotenv import load_dotenv
from google.oauth2 import service_account
from google.auth.transport.requests import Request


load_dotenv()
# llm = ChatGoogleGenerativeAI(model="gemini-3.1-flash-lite-preview", temperature=1)

# Kết nối Redis
r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
ACTIVE_SPACES_KEY = "vitex_active_spaces"


# simple_chain = llm | StrOutputParser()

# async def call_llm(message: str):
#     try:
#         return await simple_chain.ainvoke(message)
#     except Exception as e:
#         return f"Lỗi rồi Darwin ơi: {e}"

def get_token():    
    # Nối với tên file JSON
    SERVICE_ACCOUNT_FILE = os.getenv("SERVICE_ACCOUNT_FILE")
    
    print(f"🔍 Đang tìm file tại: {SERVICE_ACCOUNT_FILE}")
    # Đường dẫn tới file JSON bạn vừa tải về
    SCOPES = ['https://www.googleapis.com/auth/chat.bot']

    # Khởi tạo Credentials từ file JSON
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES
    )

    # Refresh để lấy Token mới
    creds.refresh(Request())
    
    # Return token
    return creds.token

async def broadcast_message(type="morning"):
    print(f"⏰ [{datetime.now()}] Bắt đầu gửi tin nhắn: {type}")
    
    token = get_token()
    active_spaces = r.smembers(ACTIVE_SPACES_KEY)
    
    if not active_spaces:
        print("❌ Không tìm thấy Space nào trong Redis.")
        return

    # Tùy chỉnh nội dung theo buổi
    if type == "morning":
        message_text = "Chào buổi sáng anh em Vitex! Chúc mọi người một ngày làm việc thật hiệu quả và tràn đầy năng lượng nhé! 🚀"
    else:
        message_text = "Đã 5h chiều rồi anh em ơi! Vào họp thôi cả nhà ơi"

    #message_text = await call_llm(prompt)

    async with httpx.AsyncClient() as client:
        for space_id in active_spaces:
            url = f"https://chat.googleapis.com/v1/{space_id}/messages"
            headers = {"Authorization": f"Bearer {token}"}
            try:
                await client.post(url, json={"text": message_text}, headers=headers)
                print(f"✅ Đã gửi tới {space_id}")
            except Exception as e:
                print(f"🔥 Lỗi khi gửi tới {space_id}: {e}")

async def main():
    scheduler = AsyncIOScheduler()

    # CẤU HÌNH QUAN TRỌNG: day_of_week='mon-fri' để bỏ qua Thứ 7, Chủ Nhật
    
    # 1. Chào buổi sáng lúc 8:00 (Thứ 2 -> Thứ 6)
    scheduler.add_job(
        broadcast_message, 
        'cron', 
        day_of_week='mon-fri', 
        hour=8, 
        minute=0, 
        args=["morning"],
        misfire_grace_time=300
    )

    # 2. Tạm biệt lúc 17:00 (Thứ 2 -> Thứ 6)
    scheduler.add_job(
        broadcast_message, 
        'cron', 
        day_of_week='mon-fri', 
        hour=17, 
        minute=0, 
        args=["afternoon"],
        misfire_grace_time=300
    )

    scheduler.start()
    print("🚀 Worker đã sẵn sàng! Lịch trình: 8h sáng & 5h chiều (T2-T6).")
    
    # Giữ cho script luôn chạy ngầm
    try:
        while True:
            await asyncio.sleep(1)
    except (KeyboardInterrupt, SystemExit):
        pass

if __name__ == "__main__":
    asyncio.run(main())