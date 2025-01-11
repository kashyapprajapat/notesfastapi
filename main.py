from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from typing import List
from pymongo import MongoClient
from bson import ObjectId
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates



app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")




MONGODB_URI = "mongodb+srv://kashyap:kashyap14@cluster0.jp9de.mongodb.net/notes"
client = MongoClient(MONGODB_URI)
db = client["notes"]  
notes_collection = db["notes"]  


# Helper function to serialize MongoDB ObjectId
def serialize_note(note):
    return {
        "id": str(note["_id"]),
        "title": note["title"],
        "content": note["content"]
    }


# Pydantic model for request validation
class NoteCreate(BaseModel):
    title: str
    content: str


class NoteUpdate(BaseModel):
    title: str = None
    content: str = None


@app.get("/", response_class=HTMLResponse)
async def read_item(request: Request):
    return templates.TemplateResponse(
        request=request, name="index.html"
    )


@app.get("/notes", response_model=List[dict])
async def get_notes():
    """
    Get all notes.
    """
    notes = notes_collection.find()
    return [serialize_note(note) for note in notes]


@app.get("/notes/{note_id}", response_model=dict)
async def get_note(note_id: str):
    """
    Get a single note by ID.
    """
    note = notes_collection.find_one({"_id": ObjectId(note_id)})
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    return serialize_note(note)


@app.post("/notes", response_model=dict, status_code=201)
async def create_note(note: NoteCreate):
    """
    Create a new note.
    """
    result = notes_collection.insert_one(note.dict())
    created_note = notes_collection.find_one({"_id": result.inserted_id})
    return serialize_note(created_note)


@app.put("/notes/{note_id}", response_model=dict)
async def update_note(note_id: str, note: NoteUpdate):
    """
    Update a note by ID.
    """
    update_data = {key: value for key, value in note.dict().items() if value is not None}
    if not update_data:
        raise HTTPException(status_code=400, detail="No data provided for update")

    result = notes_collection.update_one({"_id": ObjectId(note_id)}, {"$set": update_data})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Note not found")

    updated_note = notes_collection.find_one({"_id": ObjectId(note_id)})
    return serialize_note(updated_note)


@app.delete("/notes/{note_id}", status_code=204)
async def delete_note(note_id: str):
    """
    Delete a note by ID.
    """
    result = notes_collection.delete_one({"_id": ObjectId(note_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Note not found")
    return {"message": "Note deleted successfully"}
