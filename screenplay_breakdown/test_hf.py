from types import SimpleNamespace
from parser.llm_HF_mistral import enrich_scene_with_llm
from parser.llm_openrouter import enrich_scene_with_llm

scene = SimpleNamespace(
    scene_id="TEST_001",
    location_name="OFFICE",
    time_of_day="DAY",
    raw_text="INT. OFFICE - DAY. John enters and looks around nervously.",
    characters=["John"],
    props_candidates=[],
    location_candidates=[],
    character_candidates=[],
    vehicles_candidates=[],
    animals_candidates=[],
    scene_tone={"labels": ["tense", "suspenseful"], "scores": [0.9, 0.8]}
)

result = enrich_scene_with_llm(scene)
print(result)