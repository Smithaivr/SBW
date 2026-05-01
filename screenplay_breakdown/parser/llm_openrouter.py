import os
import json
import time
import requests
from jinja2 import Environment, FileSystemLoader

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
MODEL_NAME = "google/gemma-3-4b-it:free"

env = Environment(loader=FileSystemLoader("templates"))
template = env.get_template("scene_prompt.jinja")

def build_llm_prompt(scene):
    return template.render(
        scene_id=scene.scene_id,
        location_type=scene.location_type,
        location_name=scene.location_name,
        time_of_day=scene.time_of_day,
        script_pages=f"{scene.page_start}-{scene.page_end}",
        characters=scene.characters,
        props=scene.props[:10],
        vehicles=scene.vehicles[:10],
        animals=scene.animals[:10],
        action_lines=scene.action_lines,
        dialogue=[{"character": d.character, "text": d.text} for d in scene.dialogue],
        raw_text=scene.raw_text
    )


def call_llm(prompt: str, retries: int = 3) -> str:
    if not OPENROUTER_API_KEY:
        print("OpenRouter error: OPENROUTER_API_KEY not found")
        return "{}"

    for attempt in range(retries):
        try:
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": MODEL_NAME,
                    "messages": [
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.2,
                    "max_tokens": 1500,
                },
                timeout=60,
            )

            if response.status_code == 429:
                wait_time = 30 * (attempt + 1)
                print(f"Rate limited. Waiting {wait_time}s before retry {attempt + 1}/{retries}...")
                time.sleep(wait_time)
                continue

            response.raise_for_status()
            data = response.json()
            time.sleep(3)
            return data["choices"][0]["message"]["content"]

        except Exception as e:
            print(f"OpenRouter error: {e}")
            return "{}"

    print("All retries exhausted.")
    return "{}"

def parse_llm_json(raw_response: str) -> dict:
    try:
        raw_response = raw_response.strip()

        # Remove markdown fences if model returns ```json ... ```
        if raw_response.startswith("```"):
            raw_response = raw_response.replace("```json", "").replace("```", "").strip()

        return json.loads(raw_response)

    except Exception as e:
        print(f"JSON parse error: {e}")
        print("Raw LLM response:", raw_response)
        return {}


def enrich_scene_with_llm(scene):
    time.sleep(5)  # wait 5 seconds before each scene
    prompt = build_llm_prompt(scene)
    raw_response = call_llm(prompt)
    parsed = parse_llm_json(raw_response)

    if not parsed:
        return scene
             
    # Only update characters if LLM found more than regex+spaCy
    llm_characters = parsed.get("characters", [])
    for c in llm_characters:
        c_upper = c.upper()
        if c_upper not in scene.characters:
            scene.characters.append(c_upper)

    if parsed.get("props"):
        scene.props = parsed["props"]
    
    if parsed.get("vehicles"):
        scene.vehicles = parsed["vehicles"]
    
    if parsed.get("animals"):
        scene.animals = parsed["animals"]

    if parsed.get("shots"):
        scene.shot_rows = parsed["shots"]
    
    if parsed.get("action_beats"):
        scene.action_beats = parsed["action_beats"]

    return scene