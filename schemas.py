from pydantic import BaseModel
from typing import List

class GeneratedTextCreate(BaseModel):
    prompt: str

class GeneratedTextResponse(BaseModel):
    id: int
    prompt: str
    summary: str
    key_points: List[str]
    sentiment: str

    model_config = {
        "from_attributes": True
    }