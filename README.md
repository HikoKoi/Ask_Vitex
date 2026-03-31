# Ask_Vitex - Trợ lý ảo quy chế nội bộ

## Mô tả

Ask_Vitex là một dự án chatbot thông minh được tích hợp trên nền tảng Google Chat, giúp nhân viên công ty Vitex tra cứu nhanh chóng và chính xác các quy chế, quy định nội bộ dựa trên dữ liệu thực tế. Hệ thống sử dụng công nghệ RAG (Retrieval-Augmented Generation) để đảm bảo câu trả lời luôn bám sát tài liệu gốc.

## Tính năng nổi bật

- Tích hợp trên nền tảng Google Chat
- Hỗ trợ tra cứu quy chế, quy định nội bộ
- Sử dụng công nghệ RAG để đảm bảo câu trả lời luôn bám sát tài liệu gốc
- Tốc độ phản hồi nhanh
- Độ chính xác cao

## Công nghệ sử dụng

- Python 3.11.9
- LangChain
- HuggingFace
- FAISS
- Google Chat

## Kiến trúc hệ thống

- ├── data/               # Chứa các file quy chế (.pdf, .docx)
- ├── faiss_db/           # Kho lưu trữ vector sau khi nạp dữ liệu
- ├── src/
- │   ├── ingestion.py    # Module xử lý nạp dữ liệu
- │   └── rag_engine.py   # Module logic RAG và LangChain
- ├── main.py             # FastAPI Webhook cho Google Chat
- ├── .env                # Lưu trữ GOOGLE_API_KEY
- └── pyproject.toml      # Cấu hình thư viện Poetry

## Hướng dẫn sử dụng

### 1. Cài đặt môi trường

```bash
poetry install
```

### 2. Tạo file .env

```bash
GOOGLE_API_KEY=your_gemini_api_key_here
```

### 3. Nạp dữ liệu

```bash
poetry run python src/ingestion.py
```

### 4. Chạy ứng dụng

```bash
poetry run python main.py
```

### 5. Tạo webhook cho Google Chat

```bash
ngrok http 8000
```

### 6. Cấu hình Google Chat

Copy URL từ Ngrok (ví dụ: https://xyz.ngrok-free.app/webhook) và dán vào phần cấu hình App URL trong Google Chat API




