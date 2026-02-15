import os
from fastapi import APIRouter, UploadFile, HTTPException
from ..database import db
from ..config import STORAGE_BASE

router = APIRouter()

def safe_name(name):
    return os.path.basename(name)

def rename_if_exists(path):
    base, ext = os.path.splitext(path)
    counter = 1
    new_path = path
    while os.path.exists(new_path):
        new_path = f"{base}-{counter}{ext}"
        counter += 1
    return new_path

@router.post("/upload/{token}")
async def upload_file(token: str, file: UploadFile):
    link = await db.share_links.find_one({"token": token})
    if not link:
        raise HTTPException(status_code=404, detail="Invalid link")

    if link["role"] not in ["edit", "full"]:
        raise HTTPException(status_code=403, detail="Upload not allowed")

    gallery = await db.galleries.find_one({"_id": link["gallery_id"]})
    if not gallery:
        raise HTTPException(status_code=404, detail="Gallery not found")

    gallery_path = os.path.join(STORAGE_BASE, gallery["folder_name"])

    if link["folder_scope"] == "guest_uploads_only":
        subfolder = "Guest Uploads"
    else:
        if file.content_type.startswith("video"):
            subfolder = "Video"
        else:
            subfolder = "Wedding Images"

    dest_dir = os.path.join(gallery_path, subfolder)
    os.makedirs(dest_dir, exist_ok=True)

    dest_path = rename_if_exists(os.path.join(dest_dir, safe_name(file.filename)))

    with open(dest_path, "wb") as buffer:
        while chunk := await file.read(10 * 1024 * 1024):
            buffer.write(chunk)

    return {"status": "uploaded"}