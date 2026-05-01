from huggingface_hub import InferenceClient
import os
import json
import re
import time


client = InferenceClient(
    model="HuggingFaceH4/zephyr-7b-beta",
    token=os.getenv("HF_TOKEN")
)

def call_llm(prompt):
    response = client.chat_completion(
        messages=[
            {"role": "user", "content": prompt}
        ],
        max_tokens=500,
        temperature=0.2
    )

    return response.choices[0].message.content

def build_llm_prompt(scene):
    raw_text = scene.raw_text or ""
    if len(raw_text) > 1000:
        raw_text = raw_text[:1000] + "\n...[truncated]"

    props = (scene.props_candidates or [])[:3]
    vehicles = (scene.vehicles_candidates or [])[:3]
    animals = (scene.animals_candidates or [])[:3]
    tone = (scene.scene_tone or {}).get("labels", [])[:2]

    return f"""<s>[INST]
You are a film pre-production assistant.
Return STRICT JSON only. No markdown. No explanation.

Scene: {scene.scene_id} | {scene.location_name} | {scene.time_of_day}
Characters: {scene.characters}
Tone: {tone}
Props candidates: {props}
Vehicles candidates: {vehicles}
Animals candidates: {animals}

TEXT:
{raw_text}

Return JSON with exactly these keys:
{{
  "props": [],
  "vehicles": [],
  "animals_creatures": [],
  "costumes_wardrobe": [],
  "action_beats": [],
  "scene_summary": "",
  "story_function": "",
  "importance_score": 0.0
}}
[/INST]</s>"""


def call_llm(prompt: str) -> str:
    try:
        response = client.chat_completion(
            messages=[
                {"role": "user", "content": prompt}
            ],
            max_tokens=500,
            temperature=0.1
        )

        time.sleep(2)

        return response.choices[0].message.content

    except Exception as e:
        print(f"HuggingFace error: {e}")
        return "{}"


def parse_llm_response(raw: str) -> dict:
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