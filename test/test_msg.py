from json import dumps
from httplib2 import Http
from src.rag_engine import ask_vitex

# Copy the webhook URL from the Chat space where the webhook is registered.
# The values for SPACE_ID, KEY, and TOKEN are set by Chat, and are included
# when you copy the webhook URL.

def main():
    """Google Chat incoming webhook quickstart."""
    url = "https://chat.googleapis.com/v1/spaces/AAQA4qwph3Q/messages?key=AIzaSyDdI0hCZtE6vySjMm-WEfRq3CPzqKqqsHI&token=XGZgqgZ04by12UK_W9pszJoI9IHWmUmO2mIf5AX-Dgk"
    app_message = {
        "text": ask_vitex("Phương pháp làm việc của Vitex là gì?")
    }
    message_headers = {"Content-Type": "application/json; charset=UTF-8"}
    http_obj = Http()
    response = http_obj.request(
        uri=url,
        method="POST",
        headers=message_headers,
        body=dumps(app_message),
    )
    print(response)


if __name__ == "__main__":
    main()