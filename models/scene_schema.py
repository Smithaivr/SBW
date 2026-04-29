# Pydantic model representing a single scene
# Fields: scene_number, location_type, location_name, time_of_day,
# characters (list), dialogue (list of dict with character and text),
# props (list), action_summary, page_number
# This is the data structure returned by the parser

from pydantic import BaseModel
from typing import List, Optional, Literal

# Define a Dialogue model with character and text
class Dialogue(BaseModel):
    character: str
    text: str

class Scene(BaseModel):
    scene_number: int
    location_type: Literal["INT", "EXT", "INT/EXT", "EXT/INT"]
    location_name: str
    time_of_day: str  # DAY, NIGHT, DUSK, etc.
    characters: List[str]
    dialogue: List[Dialogue]
    props: Optional[List[str]] = None
    action_summary: Optional[str] = None
    page_start: Optional[int] = None
    page_end: Optional[int] = None
    raw_text: Optional[str] = None
    action_lines: List[str] = []
    scene_id: str  # e.g. "SC_001", "SC_002"
    locations_candidates: Optional[List[str]] = None
    props_candidates: Optional[List[str]] = None
    vehicles_candidates: Optional[List[str]] = None
    animals_candidates: Optional[List[str]] = None
    scene_tone: Optional[dict] = None
    llm_output: Optional[dict] = None

class Script(BaseModel):
    script_id: str                    # e.g. "ajeya_act1"
    title: Optional[str] = None       # extracted from first page or user provided
    total_pages: Optional[int] = None # total pages from PDF
    total_scenes: int                 # count of parsed scenes
    detected_format: str              # "screenplay_pdf", "screenplay_text", "screenplay_fdx"
    status: str = "parsed"            # parsed, enriched, complete
    scenes: List[Scene]               # all parsed scenes




