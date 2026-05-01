# NLP enrichment using spaCy
# Extracts characters and locations from action lines
# Used to supplement regex-based character detection
# Runs BEFORE LLM enrichment to reduce API calls

import spacy
import re

# Load English model
nlp = spacy.load("en_core_web_sm")


def extract_locations_from_action_lines(action_lines: list[str]) -> list[str]:
    # Extracts GPE and LOC entities from action lines
    # Useful for continuity tracking across scenes

    locations = []

    for line in action_lines:
        doc = nlp(line)
        for ent in doc.ents:
            if ent.label_ in ("GPE", "LOC"):
                loc = ent.text.strip()
                if loc not in locations:
                    locations.append(loc)

    return locations


def extract_props_candidates(action_lines) -> list[str]:

    EXCLUDED_PROPS = {
        "man", "men", "people", "land", "time", "wall",
        "scene", "area", "room", "face", "eyes", "body"
    }

    props = set()

    for line in action_lines:
        doc = nlp(line)

        for chunk in doc.noun_chunks:
            text = chunk.text.strip().lower()

            # remove single-word junk
            if len(text.split()) == 1:
                continue

            # remove chunks containing verbs
            if any(token.pos_ == "VERB" for token in chunk):
                continue

            # remove proper names (characters)
            if any(token.pos_ == "PROPN" for token in chunk):
                continue

            # remove pronoun-based chunks
            if text.split()[0] in {"his", "her", "their", "the", "this", "that"}:
                continue

            # keep only noun-based chunks
            if not any(token.pos_ in {"NOUN", "PROPN"} for token in chunk):
                continue

            # clean text
            text = text.strip(",.()\"'")

            # filter short / generic
            if len(text) > 2 and text not in EXCLUDED_PROPS:
                props.add(text)

    return sorted(props)
    

def extract_vehicles_candidates(text: str) -> list[str]:
    vehicle_keywords = {
        "horse", "horses", "rider", "riders",
        "cart", "carriage", "chariot", "wagon",
        "boat", "ship", "car", "truck"
    }

    found = set()
    text_lower = text.lower()

    for vehicle in vehicle_keywords:
        if re.search(rf"\b{vehicle}\b", text_lower):
            found.add(vehicle)

    return list(found)

def extract_animals_candidates(text: str) -> list[str]:
    animal_keywords = {
        "horse", "horses", "sheep", "dog", "dogs",
        "bird", "birds", "cow", "cows", "elephant", "elephants"
    }

    found = set()
    text_lower = text.lower()

    for animal in animal_keywords:
        if re.search(rf"\b{animal}\b", text_lower):
            found.add(animal)

    return list(found)


def enrich_scene_with_nlp(scene):
    text = " ".join(scene.action_lines)

    scene.props = extract_props_candidates(scene.action_lines)
    scene.vehicles = extract_vehicles_candidates(text)
    scene.animals = extract_animals_candidates(text)
    scene.locations = extract_locations_from_action_lines(scene.action_lines)

    return scene