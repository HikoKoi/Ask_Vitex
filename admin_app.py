import streamlit as st
import redis
import json
import os
import shutil
from src.ingestion import run_ingestion
from dotenv import load_dotenv
from datetime import datetime
# Nạp biến môi trường từ file .env
load_dotenv() 

# Kết nối Redis
r = redis.Redis(host=os.getenv("REDIS_HOST", "localhost"), port=6379, db=0, decode_responses=True)

st.set_page_config(page_title="Vitex Admin", layout="wide")
st.title("🛡️ Vitex Agent Admin Panel")

tab1, tab2, tab3 = st.tabs(["📚 Quản lý Tri thức", "⏰ Lịch thông báo", "💬 Lịch sử Chat"])

# --- TAB 1: UPLOAD FILE & INGESTION ---
with tab1:
    DATA_PATH = "data"
    if not os.path.exists(DATA_PATH):
        os.makedirs(DATA_PATH)

    st.header("Nạp tài liệu mới")

    st.subheader("➕ Thêm tài liệu")
    uploaded_files = st.file_uploader("Kéo thả file PDF hoặc Docx vào đây", type=['pdf', 'docx'], accept_multiple_files=True)
    
    if st.button("📥 Lưu file vào hệ thống"):
        if uploaded_files:
            for uploaded_file in uploaded_files:
                with open(os.path.join(DATA_PATH, uploaded_file.name), "wb") as f:
                    f.write(uploaded_file.getbuffer())
            st.success(f"Đã lưu {len(uploaded_files)} file vào hệ thống!")
            st.rerun()
        else:
            st.warning("Vui lòng chọn ít nhất 1 file.")
    st.divider()
    st.subheader("📂 Danh sách tài liệu")
    existing_files = [f for f in os.listdir(DATA_PATH) if f.endswith(('.pdf', '.docx'))]
    if not existing_files:
        st.info("Chưa có tài liệu nào.")
    else:
        for file in existing_files:
            col_name, col_size, col_action = st.columns([4, 1, 1])
            col_name.write(file)
            col_size.write(f"{os.path.getsize(os.path.join(DATA_PATH, file)) / 1024:.2f} KB")
            if col_action.button("Xóa", key=file):
                os.remove(os.path.join(DATA_PATH, file))
                st.rerun()
    st.divider()
    st.subheader("🔄 Cập nhật tri thức")
    st.info("Nhấn nút dưới đây để xử lý và update tri thức.")
    if st.button("🚀 Bắt đầu cập nhật", type="primary"):
        with st.spinner("Đang xử lý tài liệu..."):
            try:
                run_ingestion()
                st.success("Đã xử lý xong!")
            except Exception as e:
                st.error(f"Lỗi: {e}")
# --- TAB 2: QUẢN LÝ LỊCH HẸN (REDIS) ---
with tab2:
    st.header("Cấu hình thông báo tự động")
    
    # Form thêm lịch mới
    with st.expander("➕ Thêm lịch thông báo mới"):
        col1, col2 = st.columns(2)
        with col1:
            time_input = st.text_input("Nhập giờ thông báo (Định dạng HH:mm)", placeholder="Ví dụ: 08:30 hoặc 17:00")
            job_type = st.selectbox("Loại tin nhắn", ["morning", "afternoon", "lunch", "custom"])
        with col2:
            job_days = st.multiselect("Ngày trong tuần", ["mon", "tue", "wed", "thu", "fri", "sat", "sun"], default=["mon", "tue", "wed", "thu", "fri"])
            custom_msg = st.text_input("Nội dung tùy chỉnh (nếu chọn loại custom)")

        if st.button("Lưu lịch hẹn"):
            try:
                if ":" not in time_input:
                    st.error("Định dạng giờ không hợp lệ. Vui lòng nhập HH:mm (ví dụ: 08:30)")
                    st.stop()
                # Parse giờ từ chuỗi HH:mm
                job_time = datetime.strptime(time_input, "%H:%M")
            except ValueError:
                st.error("Định dạng giờ không hợp lệ. Vui lòng nhập HH:mm (ví dụ: 08:30)")
                st.stop()
            job_id = f"job_{job_time.strftime('%H%M')}"
            job_data = {
                "id": job_id,
                "hour": job_time.hour,
                "minute": job_time.minute,
                "days": ",".join(job_days),
                "type": job_type,
                "msg": custom_msg
            }
            # Lưu vào Redis Hash để Worker đọc
            r.hset("vitex_schedules", job_id, json.dumps(job_data))
            st.success(f"Đã lưu lịch lúc {job_time}!")

    # Hiển thị danh sách lịch hiện có
    st.subheader("Danh sách lịch đã lên")
    schedules = r.hgetall("vitex_schedules")
    for j_id, j_json in schedules.items():
        j = json.loads(j_json)
        col_text, col_btn = st.columns([4, 1])
        col_text.write(f"⏰ **{j['hour']:02d}:{j['minute']:02d}** | Loại: {j['type']} | Ngày: {j['days']}")
        if col_btn.button("Xóa", key=j_id):
            r.hdel("vitex_schedules", j_id)
            st.rerun()

# --- TAB 3: THREAD ID & HISTORY ---
with tab3:
    st.header("Các Thread đang hoạt động")
    # Lấy tất cả key không phải là cấu hình hệ thống
    keys = r.keys("spaces/*/threads/*") # Pattern của Google Chat thread
    if not keys:
        st.info("Chưa có lịch sử hội thoại nào.")
    else:
        selected_thread = st.selectbox("Chọn Thread ID để xem nội dung", keys)
        if selected_thread:
            history = r.lrange(selected_thread, 0, -1)
            qna = []
            for msg in history[::-1]:
                qna.append(msg)
                if len(qna) == 2:
                    st.text(qna[1])
                    st.text(qna[0])
                    qna = []
                    st.divider()
