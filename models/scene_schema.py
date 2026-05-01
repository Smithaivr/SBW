from pydantic import BaseModel, Field
from typing import List, Optional, Literal

class Dialogue(BaseModel):
    character: str
    text: str

class Shot(BaseModel):
    shot_id: str
    shot_type: str
    description: str
    camera_perspective: Optional[str] = None
    storyboard_panel: Optional[str] = None

class Scene(BaseModel):
    scene_id: str
    scene_number: int
    location_type: Literal["INT", "EXT", "INT/EXT", "EXT/INT"]
    location_name: str
    time_of_day: str
    characters: List[str] = []
    dialogue: List[Dialogue] = []
    action_lines: List[str] = []
    action_beats: List[str] = Field(default_factory=list)
    page_start: Optional[int] = None
    page_end: Optional[int] = None
    raw_text: Optional[str] = None
    # All enriched fields — populated progressively by NLP then LLM
    locations: Optional[List[str]] = None
    props: Optional[List[str]] = None
    vehicles: Optional[List[str]] = None
    animals: Optional[List[str]] = None
    special_effects: Optional[List[str]] = None
    continuity_references: List[str] = Field(default_factory=list)
    camera_perspective: List[str] = Field(default_factory=list)
    shot_rows: List[dict] = Field(default_factory=list)
    action_summary: Optional[str] = None
    emotional_tone: Optional[dict] = None

class Script(BaseModel):
    script_id: str
    title: Optional[str] = None
    total_pages: Optional[int] = None
    total_scenes: int
    detected_format: str
    status: str = "parsed"
    scenes: List[Scene]