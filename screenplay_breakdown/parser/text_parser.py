# Parse plain text or Fountain format screenplay
# Split script into scenes by detecting INT. or EXT. slug lines using regex
# For each scene extract:
#   - scene_number (auto increment)
#   - location_type (INT or EXT) using regex
#   - location_name (text between INT/EXT and time of day) using regex
#   - time_of_day (DAY, NIGHT, DUSK etc) using regex
#   - characters (ALL CAPS lines that are not scene headings or transitions)
#   - dialogue (lines immediately following a character cue)
#   - page_number (if present, else None)
# Return list of scene dicts matching the Scene model

from models.scene_schema import Scene, Dialogue
from parser.nlp_enricher import enrich_scene_with_nlp
from typing import List
import re   

def parse_text_script(pages: list[tuple[int, str]]) -> list[Scene]:
    scenes = []
    current_page = 1

    EXCLUDED_CAPS = {
        "FADE IN", "FADE OUT", "CUT TO", "BACK TO", "MONTAGE",
        "SMASH CUT", "DISSOLVE TO", "TITLE CARD", "SUPER",
        "INTERCUT", "END OF", "CONT'D",
        "ARENA", "FORT GATES", "REAR WALL", "CLIFF",
        "COURT ROOM", "OPEN AREA"
    }

    scene_number = 1
    
    current_scene = None
    current_character = None
    dialogue_buffer = []

    for page_number, page_text in pages:
        current_page = page_number
        for line in page_text.splitlines():
            line = line.strip()

            # Skip empty lines
            if not line:
                continue

            # Check for scene heading (slug line)
            scene_heading_match = re.match(r'^(INT\.?|EXT\.?|INT\./EXT\.?|EXT\./INT\.?)\s+(.*)', line)
            if scene_heading_match:
                # If we were processing a previous scene, save it before starting a new one
                if current_scene:
                    if dialogue_buffer and current_character:
                        current_scene.dialogue.append(
                            Dialogue(character=current_character, text=" ".join(dialogue_buffer))
                        )
                    scenes.append(current_scene)
                
                location_type_raw, rest = scene_heading_match.groups()
                location_type_raw, rest = scene_heading_match.groups()
                location_type = location_type_raw.replace(".", "")

                parts = [p.strip() for p in rest.split("-")]
                time_of_day = parts[-1]
                location_name = " - ".join(parts[:-1])

                parts = [p.strip() for p in rest.split("-")]
                time_of_day = parts[-1]
                location_name = " - ".join(parts[:-1])

                if current_scene:
                    current_scene.page_end = current_page

                current_scene = Scene(
                    scene_id=f"SC_{scene_number:03d}",  # SC_001, SC_002 etc
                    scene_number=scene_number,
                    location_type=location_type,
                    location_name=location_name.strip(),
                    time_of_day=time_of_day,
                    characters=[],
                    dialogue=[],
                    action_lines=[],
                    page_start=current_page,
                    page_end=None,
                    raw_text=""
                )
                scene_number += 1
                current_character = None
                dialogue_buffer = []
                continue

            if not current_scene:
                continue

            current_scene.raw_text += line + "\n"
            
            # Character cue (allow (V.O.), (O.S.), (cont'd))
            is_character_cue = (
                re.match(r"^[A-Z][A-Z\s'\(\)\.]+$", line)
                and not line.endswith(".")
                and len(line.split()) <= 4
            )

            if is_character_cue:
                
                clean_character = re.sub(r'\s*\(.*?\)', '', line).strip()
                if clean_character in EXCLUDED_CAPS:
                    current_character = None
                    
                    continue

                if dialogue_buffer and current_character:
                    current_scene.dialogue.append(Dialogue(character=current_character, text=" ".join(dialogue_buffer)))

                current_character = clean_character
                dialogue_buffer = []

                if current_character not in current_scene.characters:
                    current_scene.characters.append(current_character)

                continue
    
            # Dialogue lines
            if current_character:
                if re.match(r'^\(.*\)$', line):
                    continue
                dialogue_buffer.append(line)
            else:
                current_scene.action_lines.append(line)
            
    
    # Append the last scene if it exists
    if current_scene:
        if dialogue_buffer and current_character:
            current_scene.dialogue.append(
                Dialogue(character=current_character, text=" ".join(dialogue_buffer)
            ))
        current_scene.page_end = current_page
        scenes.append(current_scene)
    
    return scenes

if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python -m parser.text_parser <txt_path>")
        sys.exit(1)

    txt_path = sys.argv[1]

    with open(txt_path, "r", encoding="utf-8") as f:
        script_text = f.read()

    pages = [(1, script_text)]
    scenes = parse_text_script(pages)
    scenes = [enrich_scene_with_nlp(scene) for scene in scenes]

    output_path = "samples/ajeya_parsed.txt"

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(f"Total scenes: {len(scenes)}\n\n")

        for scene in scenes:
            f.write(f"{'='*40}\n")
            f.write(f"Scene {scene.scene_number}\n")
            f.write(f"{'='*40}\n")

            f.write(f"location_type: {scene.location_type}\n")
            f.write(f"location_name: {scene.location_name}\n")
            f.write(f"time_of_day: {scene.time_of_day}\n\n")
            f.write(f"page_start: {scene.page_start}\n")
            f.write(f"page_end: {scene.page_end}\n\n")

            f.write("characters:\n")
            for c in scene.characters:
                f.write(f"- {c}\n")

            f.write("\ndialogue:\n")
            for d in scene.dialogue:
                f.write(f"{d.character}: {d.text}\n")

            f.write("\naction_lines:\n")
            for a in scene.action_lines:
                f.write(f"- {a}\n")

            f.write("\nprops_candidates:\n")
            for p in scene.props_candidates or []:
                f.write(f"- {p}\n")

            f.write("\nvehicles_candidates:\n")
            for v in scene.vehicles_candidates or []:
                f.write(f"- {v}\n")

            f.write("\nanimals_candidates:\n")
            for a in scene.animals_candidates or []:
                f.write(f"- {a}\n")

            f.write("\nlocations_candidates:\n")
            for l in scene.locations_candidates or []:
                f.write(f"- {l}\n")

            f.write("\n\n")

    print(f"Output saved to {output_path}")