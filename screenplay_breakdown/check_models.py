import requests
import os
from dotenv import load_dotenv

load_dotenv()

response = requests.get(
    "https://openrouter.ai/api/v1/models",
    headers={
        "Authorization": f"Bearer {os.getenv('OPENROUTER_API_KEY')}"
    }
)

models = response.json()
for model in models["data"]:
    if "free" in model["id"].lower():
        print(model["id"])