import os
import httpx
import redis
from google.oauth2 import service_account
from google.auth.transport.requests import Request
from datetime import datetime
from dotenv import load_dotenv

# Nạp biến môi trường từ file .env
load_dotenv() 

# Cấu hình Redis
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
r = redis.Redis(host=REDIS_HOST, port=6379, db=0, decode_responses=True)
ACTIVE_SPACES_KEY = "vitex_active_spaces"

def get_token():    
    """Lấy Access Token từ Service Account"""
    SERVICE_ACCOUNT_FILE = os.getenv("SERVICE_ACCOUNT_FILE")
    if not SERVICE_ACCOUNT_FILE or not os.path.exists(SERVICE_ACCOUNT_FILE):
        print(f"❌ Lỗi: Không thấy file {SERVICE_ACCOUNT_FILE}")
        return None

    SCOPES = ['https://www.googleapis.com/auth/chat.bot']
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES
    )
    creds.refresh(Request())
    return creds.token

async def send_message(space_id, text):
    """Gửi tin nhắn tới 1 không gian cụ thể"""
    token = get_token()
    if not token: return
    
    url = f"https://chat.googleapis.com/v1/{space_id}/messages"
    headers = {"Authorization": f"Bearer {token}"}
    async with httpx.AsyncClient() as client:
        try:
            res = await client.post(url, json={"text": text}, headers=headers)
            return res.status_code == 200
        except Exception as e:
            print(f"🔥 Lỗi gửi tin: {e}")
            return False

async def broadcast_message(job_type="morning", custom_msg=None):
    """Gửi thông báo tới toàn bộ các Space đã lưu trong Redis"""
    print(f"⏰ [{datetime.now()}] Thực thi Job: {job_type}")
    
    # 1. Xác định nội dung
    if job_type == "morning":
        msg = "☀️ Chào buổi sáng anh em Vitex! Chúc mọi người ngày mới năng lượng."
    elif job_type == "lunch":
        msg = "🍜 Đến giờ đặt cơm trưa rồi anh em ơi!"
    elif job_type == "afternoon":
        msg = "🏠 Đã 5h chiều rồi, chuẩn bị nghỉ ngơi thôi."
    else:
        msg = custom_msg or "🔔 Thông báo từ hệ thống Vitex Agent."

    # 2. Lấy danh sách Space và gửi
    active_spaces = r.smembers(ACTIVE_SPACES_KEY)
    for space_id in active_spaces:
        success = await send_message(space_id, msg)
        if success:
            print(f"✅ Đã gửi tới {space_id}")