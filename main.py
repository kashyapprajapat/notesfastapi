from fastapi import FastAPI, HTTPException, Request, UploadFile, File
from pydantic import BaseModel
from typing import List
from pymongo import MongoClient
from bson import ObjectId
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

import cloudinary
import cloudinary.uploader


app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


# Configure Cloudinary using CLOUDINARY_URL from .env
cloudinary.config(
    cloud_name="dpf5bkafv",
    api_key="312872495236641",
    api_secret="1ehzq6KnCU10UcqUOMe6qoN0NLc"
)

# Helper function to serialize MongoDB ObjectId
def serialize_data(data):
    return {**data, "id": str(data["_id"])}

# Function to upload image to Cloudinary
def upload_image_to_cloudinary(file: UploadFile):
    try:
        result = cloudinary.uploader.upload(file.file,
            folder="pytest",  resource_type="image")
        return result["secure_url"]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Image upload failed: {e}")



MONGODB_URI = "mongodb://kashyap:kashyap14@cluster0.jp9de.mongodb.net/notes?retryWrites=true&w=majority"
client = MongoClient(MONGODB_URI)
db = client["notes"]  
notes_collection = db["notes"]  
test_collection = db["test"] 

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

from fastapi.responses import JSONResponse

@app.post("/testimage", response_model=dict)
async def upload_and_save_image(file: UploadFile = File(...)):
    """
    Upload an image, save it to Cloudinary, and store the URL in MongoDB.
    """
    if file.content_type.split('/')[0] != "image":
        raise HTTPException(status_code=400, detail="Invalid file type. Only images are allowed.")

    # Upload image to Cloudinary
    img_url = upload_image_to_cloudinary(file)

    # Save the image URL in MongoDB
    result = test_collection.insert_one({"imgurl": img_url})
    
    # Retrieve the saved data and convert ObjectId to string
    saved_data = test_collection.find_one({"_id": result.inserted_id})
    return {
        "id": str(saved_data["_id"]),  # Convert ObjectId to string
        "imgurl": saved_data["imgurl"]
    }



# Helper function to serialize MongoDB documents
def serialize_document(document):
    return {
        "id": str(document["_id"]),
        "imgurl": document.get("imgurl", None)
    }


@app.get("/getall", response_model=List[dict])
async def get_all_data():
    """
    Retrieve all documents from the 'test' collection.
    """
    try:
        documents = test_collection.find()
        result = [serialize_document(doc) for doc in documents]
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve data: {e}")
