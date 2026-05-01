import pandas as pd
import json
import os,sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from parser.pdf_parser import extract_text_from_pdf
from parser.text_parser import parse_text_script
from models.scene_schema import Script
from parser.nlp_enricher import extract_locations_from_action_lines,enrich_scene_with_nlp
from parser.llm_openrouter import enrich_scene_with_llm
from post_processing.export_excel import build_excel_from_scene_jsons

def process_pdf_to_excel(pdf_path: str) -> str:
    # Step 1 — extract pages with numbers directly from PDF
    pages = extract_text_from_pdf(pdf_path)

    # Step 2 — pass pages directly to parser
    scenes = parse_text_script(pages)

    # Step 3 — NLP enrichment
    scenes = [enrich_scene_with_nlp(scene) for scene in scenes]

    # Step 4 — LLM enrichment
    json_files = []

    os.makedirs("outputs", exist_ok=True)

    for scene in scenes:
        try:
            scene = enrich_scene_with_llm(scene)
        except Exception as e:
            print(f"Error in scene {scene.scene_id}: {e}")
            continue

        file_path = f"outputs/scene_{scene.scene_id}.json"
        print(f"Saving current API run: {file_path}")
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(scene.model_dump(), f, indent=2)

        json_files.append(file_path)

    # Step 5 — export to Excel
    output_path = build_excel_from_scene_jsons(json_files, "output.xlsx")

    return output_path


#process_pdf_to_excel("screenplay_breakdown/samples/Ajeya_ACT_1.pdf")