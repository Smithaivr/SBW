from parser.pdf_parser import extract_text_from_pdf
from parser.text_parser import parse_text_script
from models.scene_schema import Script
from parser.nlp_enricher import extract_characters_from_action_lines, extract_locations_from_action_lines,enrich_scene_with_nlp

pdf_path = "samples/Ajeya_ACT_1.pdf"

# Step 1 — extract pages with numbers directly from PDF
pages = extract_text_from_pdf(pdf_path)

# Step 2 — pass pages directly to parser
scenes = parse_text_script(pages)
scenes = [enrich_scene_with_nlp(scene) for scene in scenes]

# Step 3 — spaCy enrichment before building Script object
for scene in scenes:
    scene.characters = extract_characters_from_action_lines(
        scene.action_lines,
        scene.characters
    )

# Step 4 — build script metadata wrapper after enrichment
script = Script(
    script_id="ajeya_act1",
    title="AJEYA",
    total_pages=len(pages),
    total_scenes=len(scenes),
    detected_format="screenplay_pdf",
    status="parsed",
    scenes=scenes
)


# Step 4 — save to file
output_path = "samples/ajeya_parsed_pdf.txt"
with open(output_path, "w", encoding="utf-8") as f:
    f.write(f"Script ID: {script.script_id}\n")
    f.write(f"Title: {script.title}\n")
    f.write(f"Total pages: {script.total_pages}\n")
    f.write(f"Total scenes: {script.total_scenes}\n")
    f.write(f"Format: {script.detected_format}\n")
    f.write(f"Status: {script.status}\n\n")
    f.write("="*40 + "\n\n")

    for scene in script.scenes:
        f.write(f"{'='*40}\n")
        f.write(f"Scene {scene.scene_id}\n")
        f.write(f"{'='*40}\n")
        f.write(f"location_type: {scene.location_type}\n")
        f.write(f"location_name: {scene.location_name}\n")
        f.write(f"time_of_day: {scene.time_of_day}\n")
        f.write(f"page_start: {scene.page_start}\n")
        f.write(f"page_end: {scene.page_end}\n\n")
        f.write("characters:\n")
        for c in scene.characters:
            f.write(f"- {c}\n")

        f.write("\nprops:\n")
        for p in scene.props_candidates or []:
            f.write(f"- {p}\n")
        f.write("\nvehicles:\n")
        for v in scene.vehicles_candidates or []:
            f.write(f"- {v}\n")

        f.write("\nanimals:\n")
        for a in scene.animals_candidates or []:
            f.write(f"- {a}\n")

        f.write("\nlocations:\n")
        for l in scene.locations_candidates or []:
            f.write(f"- {l}\n")
        f.write("\ndialogue:\n")
        for d in scene.dialogue:
            f.write(f"{d.character}: {d.text}\n")
        f.write("\naction_lines:\n")
        for a in scene.action_lines:
            f.write(f"- {a}\n")
        f.write("\n\n")

print(f"Output saved to {output_path}")