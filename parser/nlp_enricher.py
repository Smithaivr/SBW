# NLP enrichment using spaCy
# Extracts characters and locations from action lines
# Used to supplement regex-based character detection
# Runs BEFORE LLM enrichment to reduce API calls

import spacy
import re
import nltk
from transformers import pipeline
from nltk.corpus import stopwords

nltk.download('stopwords')

# Load English model
nlp = spacy.load("en_core_web_sm")

STOP_WORDS = set(stopwords.words("english"))

# load once (global)
tone_classifier = pipeline(
    "zero-shot-classification",
    model="facebook/bart-large-mnli"
)

SCREENPLAY_TONE_LABELS = [
    "romantic",
    "comic",
    "tragic",
    "suspenseful",
    "mysterious",
    "tense",
    "fearful",
    "melancholic",
    "hopeful",
    "nostalgic",
    "dramatic",
    "emotional",
    "violent",
    "action-driven",
    "reflective",
    "intimate",
    "ominous",
    "inspirational",
    "chaotic",
    "calm"
]


def extract_scene_tone(text: str):
    if not text or not text.strip():
        return None

    result = tone_classifier(
        text,
        SCREENPLAY_TONE_LABELS,
        multi_label=True   # pick best one
    )

    return {
    "labels": result["labels"][:3],   # top 2–3 tones
    "scores": [float(s) for s in result["scores"][:3]]
    }


def extract_characters_from_action_lines(action_lines: list[str], existing_characters: list[str]) -> list[str]:
    # Takes action lines from a scene and extracts PERSON entities
    # Merges with existing characters from regex detection
    # Returns deduplicated combined list

    EXCLUDED_ENTITIES = {"ROHIDA", "MAVALA", "MARATHA", "HINDUSTAN"}
    characters = list(existing_characters)  # start with regex-detected characters
    
    for line in action_lines:
        doc = nlp(line)
        for ent in doc.ents:
            if ent.label_ == "PERSON":
                # normalise to uppercase to match existing character format
                name = ent.text.strip().upper()
                if name not in EXCLUDED_ENTITIES and len(name) > 2:
                    if name not in characters:
                        characters.append(name)

    #remove substrings e.g. "BAJI" if "BAJI PRABHU" exists
    # "BAJI PRABHU" inside "BAJI PRABHU'S WIFE" → keep (possessive makes it different)
    characters = [
        c for c in characters
        if not any(c != other and c in other and not other.startswith(c + "'") for other in characters)
    ]
    return characters


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

            # remove stopword-only chunks
            if all(token.text.lower() in STOP_WORDS for token in chunk):
                continue

            # remove pronoun-based chunks
            if text.split()[0] in {"his", "her", "their", "the", "this", "that"}:
                continue

            # remove chunks containing verbs
            if any(token.pos_ == "VERB" for token in chunk):
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

    scene.locations_candidates = extract_locations_from_action_lines(scene.action_lines)
    scene.props_candidates = extract_props_candidates(scene.action_lines)
    scene.vehicles_candidates = extract_vehicles_candidates(scene.raw_text or "")
    scene.animals_candidates = extract_animals_candidates(scene.raw_text or "")
    tone_text = " ".join(scene.action_lines[:5])  # only first 5 lines
    scene.scene_tone = extract_scene_tone(tone_text)

    return scene
