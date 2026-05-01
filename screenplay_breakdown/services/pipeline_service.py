import pandas as pd
from parser.pdf_parser import extract_text_from_pdf
from parser.text_parser import parse_text_script
from models.scene_schema import Script
from parser.nlp_enricher import extract_locations_from_action_lines,enrich_scene_with_nlp
from parser.llm_openrouter import enrich_scene_with_llm
from post_processing.export_excel import export_all

def process_pdf_to_excel(pdf_path: str) -> str:
    # Step 1 — extract pages with numbers directly from PDF
    pages = extract_text_from_pdf(pdf_path)

    # Step 2 — pass pages directly to parser
    scenes = parse_text_script(pages)

    # Step 3 — NLP enrichment
    scenes = [enrich_scene_with_nlp(scene) for scene in scenes]

    # Step 4 — LLM enrichment
    scenes = [enrich_scene_with_llm(scene) for scene in scenes[:1]]
    # Step 5 — export to Excel
    output_path = export_all(scenes)

    return output_path