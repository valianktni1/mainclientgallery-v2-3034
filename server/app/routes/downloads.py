import os
import shutil
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from ..database import db
from ..config import STORAGE_BASE

router = APIRouter()

async def get_link_and_gallery(token: str):
    link = await db.share_links.find_one({"token": token})
    if not link:
        raise HTTPException(status_code=404, detail="Invalid link")

    if link["role"] not in ["read", "full"]:
        raise HTTPException(status_code=403, detail="Download not allowed")

    gallery = await db.galleries.find_one({"_id": link["gallery_id"]})
    if not gallery:
        raise HTTPException(status_code=404, detail="Gallery not found")

    return link, gallery

@router.get("/download/video/{token}/{filename}")
async def download_video(token: str, filename: str):
    link, gallery = await get_link_and_gallery(token)

    if link["folder_scope"] == "guest_uploads_only":
        raise HTTPException(status_code=403, detail="Access denied")

    path = os.path.join(STORAGE_BASE, gallery["folder_name"], "Video", filename)

    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(path, media_type="video/mp4")

@router.get("/download/images-zip/{token}")
async def download_images_zip(token: str):
    link, gallery = await get_link_and_gallery(token)

    if link["folder_scope"] == "guest_uploads_only":
        raise HTTPException(status_code=403, detail="Access denied")

    base = os.path.join(STORAGE_BASE, gallery["folder_name"])
    images_folder = os.path.join(base, "Wedding Images")
    zip_path = os.path.join(base, "generated_full_images")

    shutil.make_archive(zip_path, 'zip', images_folder)

    return FileResponse(zip_path + ".zip", media_type="application/zip")