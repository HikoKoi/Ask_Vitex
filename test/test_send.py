from google.oauth2 import service_account
from google.auth.transport.requests import Request
import httpx
import asyncio
import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import StrOutputParser

load_dotenv()
llm = ChatGoogleGenerativeAI(model="gemini-3.1-flash-lite-preview", temperature=1)

def get_token():
    # 1. Lấy đường dẫn tuyệt đối đến thư mục chứa file test_send.py (thư mục 'test')
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 2. Đi ra thư mục cha (thư mục gốc 'Ask_Vitex')
    root_dir = os.path.dirname(current_dir)
    
    # 3. Nối với tên file JSON
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

async def send_message(token, space_name, message):
    # URL google chat
    url = "https://chat.googleapis.com/v1/" + space_name + "/messages"
    
    # chat_event = event.get("chat", {})
    # space_name = chat_event.get("messagePayload", {}).get("space", {}).get("name")
    # url = "https://chat.googleapis.com/v1/" + space_name + "/messages"

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json; charset=UTF-8",
    }
    
    payload = {
        "text": message
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            print("✅ Gửi tin nhắn riêng thành công!")
        else:
            print(f"❌ Lỗi: {response.text}")

def get_poem_message(content):
    prompt = """
    Bạn là một nhà hiền triết hiện đại và tích cực chuyên làm thơ. 
    Hãy viết một bài thơ, sâu sắc và đầy cảm hứng về 
    """ + content + """. 
    Nội dung nên hướng tới việc tạo động lực làm việc, sự tử tế hoặc phát triển bản thân.
    Trình bày dưới dạng: \n Nội dung bài thơ \n -Thơ cùi từ Test-
    Không cần thêm bất cứ lời dẫn hay giải thích nào khác.
    """
    return prompt
    

simple_chain = llm | StrOutputParser()

async def call_llm(message: str):
    try:
        return await simple_chain.ainvoke(message)
    except Exception as e:
        return f"Lỗi rồi Darwin ơi: {e}"


async def main():
    # 1. Lấy token
    token = get_token()
    
    # 2. Tạo nội dung bài thơ (String)
    #prompt = get_poem_message("Chào buổi sáng năng lượng")
    
    # 3. Gọi LLM và ĐỢI (await) lấy kết quả bài thơ thực sự
    #message_text = await call_llm(prompt)
    message_text = "Chào buổi sáng năng lượng"
    # 4. Gửi tin nhắn đi
    space_id = "spaces/wUNeZSAAAAE"
    await send_message(token, space_id, message_text)

if __name__ == "__main__":
    # Kích hoạt toàn bộ quy trình
    asyncio.run(main())

