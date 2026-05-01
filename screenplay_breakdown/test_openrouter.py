import os
import requests

def call_llm(prompt):
    print("KEY FOUND:", os.getenv("OPENROUTER_API_KEY") is not None)
    print("KEY START:", (os.getenv("OPENROUTER_API_KEY") or "")[:8])
    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {os.getenv('OPENROUTER_API_KEY')}",
            "Content-Type": "application/json",
        },
        json={
            "model": "mistralai/mistral-7b-instruct:free",
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.2,
            "max_tokens": 400,
        },
        timeout=60,
    )

    print("STATUS:", response.status_code)
    print("RAW:", response.text)

    response.raise_for_status()
    data = response.json()
    return data["choices"][0]["message"]["content"]

prompt = """
Extract structured screenplay info from this scene.
Return JSON only.

Scene:
INT. OFFICE - DAY. John enters and looks around nervously.
"""

print(call_llm(prompt))