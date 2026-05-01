from google import genai
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
print(f"Key loaded: {api_key[:8]}...{api_key[-4:]}")

client = genai.Client(api_key=api_key)

try:
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents="Say hello in one word"
    )
    print("SUCCESS:", response.text)
except Exception as e:
    print("ERROR:", e)