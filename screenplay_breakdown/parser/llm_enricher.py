import json
import requests
import re

def build_llm_prompt(scene):
    return f"""
You are a film pre-production assistant.

Analyze the screenplay scene below and return STRICT JSON only.
Do not include markdown. Do not include explanation.

SCENE DATA:
scene_id: {scene.scene_id}
location: {scene.location_name}
time_of_day: {scene.time_of_day}
characters_detected: {scene.characters}
props_candidates: {scene.props_candidates}
vehicles_candidates: {scene.vehicles_candidates}
animals_candidates: {scene.animals_candidates}
scene_tone: {scene.scene_tone}

SCENE TEXT:
{scene.raw_text}

Return JSON with exactly these keys:
{{
  "shots_storyboard_panels": [],
  "characters": [],
  "locations_environments": [],
  "props": [],
  "vehicles": [],
  "animals_creatures": [],
  "costumes_wardrobe": [],
  "action_beats": [],
  "continuity_references": [],
  "camera_perspective_controls": []
}}
"""


def call_llm(prompt: str) -> str:
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "phi4",
                "prompt": prompt,
                "stream": False
            },
            timeout=120  # Phi-4 can be slow
        )

        if response.status_code == 500:
            print(f"Ollama 500 error: {response.text}")
            return "{}"

        response.raise_for_status()
        return response.json()["response"]

    except requests.exceptions.Timeout:
        print(f"Ollama timeout for scene")
        return "{}"
    except Exception as e:
        print(f"Ollama error: {e}")
        return "{}"

def parse_llm_response(raw: str) -> dict:
    # Strip markdown code fences if Phi-4 adds them
    clean = re.sub(r'^```json\s*|^```\s*|```$', '', raw.strip(), flags=re.MULTILINE)
    try:
        return json.loads(clean.strip())
    except json.JSONDecodeError:
        return {
            "error": "LLM did not return valid JSON",
            "raw_response": raw
        }

def enrich_scene_with_llm(scene):
    prompt = build_llm_prompt(scene)
    raw_response = call_llm(prompt)
    scene.llm_output = parse_llm_response(raw_response)
    return scene