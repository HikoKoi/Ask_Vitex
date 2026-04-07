import asyncio
import os
import json
import redis
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from src.message import broadcast_message # Import từ file mới

# Kết nối Redis
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
r = redis.Redis(host=REDIS_HOST, port=6379, db=0, decode_responses=True)

scheduler = AsyncIOScheduler()

async def sync_schedules_from_redis():
    """Đọc cấu hình từ Redis và cập nhật vào Scheduler"""
    print("🔄 Đang đồng bộ lịch từ Redis...")
    
    # Lấy tất cả lịch hẹn từ Hash key 'vitex_schedules'
    # Hash này được nạp dữ liệu từ trang Admin Streamlit
    schedules = r.hgetall("vitex_schedules")
    
    # Xóa các job cũ (ngoại trừ job sync này) để nạp lại từ đầu
    current_jobs = scheduler.get_jobs()
    for job in current_jobs:
        if job.id != "sync_task":
            scheduler.remove_job(job.id)

    # Nạp lịch mới
    for job_id, job_json in schedules.items():
        try:
            j = json.loads(job_json)
            scheduler.add_job(
                broadcast_message,
                'cron',
                day_of_week=j.get('days', 'mon-fri'),
                hour=j.get('hour'),
                minute=j.get('minute'),
                args=[j.get('type'), j.get('msg')],
                id=job_id,
                misfire_grace_time=300
            )
            print(f"➕ Đã nạp lịch: {j['hour']}:{j['minute']} ({j['type']})")
        except Exception as e:
            print(f"❌ Lỗi khi nạp job {job_id}: {e}")

async def main():
    # 1. Job đặc biệt: Cứ mỗi 1 phút lại kiểm tra Redis xem có lịch mới không
    scheduler.add_job(sync_schedules_from_redis, 'interval', minutes=1, id="sync_task")
    
    # 2. Chạy lần đầu ngay lập tức
    await sync_schedules_from_redis()
    
    scheduler.start()
    print("🚀 Worker đã sẵn sàng và đang lắng nghe Redis!")

    try:
        while True:
            await asyncio.sleep(1)
    except (KeyboardInterrupt, SystemExit):
        print("Stopping worker...")

if __name__ == "__main__":
    asyncio.run(main())