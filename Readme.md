## This is notes api buid while learning Fastapi.

# FastAPI MongoDB Notes & Image Upload App

A FastAPI application for managing notes and images with MongoDB Atlas integration and Cloudinary image storage.

## Features

- Create, read, update, and delete notes
- Upload images to Cloudinary
- Store image URLs in MongoDB
- Retrieve and display images

## Screenshots

![Notes App Interface](./Laptop.png)

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Serves the main HTML interface |
| `/notes` | GET | Get all notes |
| `/notes/{note_id}` | GET | Get a single note by ID |
| `/notes` | POST | Create a new note |
| `/notes/{note_id}` | PUT | Update a note by ID |
| `/notes/{note_id}` | DELETE | Delete a note by ID |
| `/testimage` | POST | Upload an image to Cloudinary and save URL to MongoDB |
| `/getall` | GET | Get all image URLs from database |

## Setup

1. Clone this repository
2. Install dependencies:
   ```
   pip install fastapi uvicorn pymongo python-multipart jinja2 cloudinary
   ```
3. Configure MongoDB connection:
   ```python
   MONGODB_URI = "mongodb+srv://username:password@cluster0.example.mongodb.net/database?retryWrites=true&w=majority"
   ```
4. Configure Cloudinary credentials:
   ```python
   cloudinary.config(
       cloud_name="your_cloud_name",
       api_key="your_api_key",
       api_secret="your_api_secret"
   )
   ```
5. Run the application:
   ```
   uvicorn main:app --host 0.0.0.0 --port 8000
   ```

## Keep learning keep doing ....
