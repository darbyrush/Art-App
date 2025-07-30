# backend/routers/feedback.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import json
import os

router = APIRouter()

class Feedback(BaseModel):
    image_url: str
    liked: bool

FEEDBACK_FILE = "feedback_data.json"

def save_feedback_to_file(feedback: Feedback):
    data = []
    if os.path.exists(FEEDBACK_FILE):
        with open(FEEDBACK_FILE, "r") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                data = []
    data.append(feedback.dict())
    with open(FEEDBACK_FILE, "w") as f:
        json.dump(data, f, indent=2)

@router.post("/feedback")
async def receive_feedback(feedback: Feedback):
    try:
        save_feedback_to_file(feedback)
        return {"message": "Feedback received"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))