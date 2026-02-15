import os
from fastapi import APIRouter, HTTPException
from ..database import db
from ..config import STORAGE_BASE, MAX_LIMIT, GUEST_LIMIT
from ..models import gallery_document, share_link_document
from ..security import hash_password

router = APIRouter()

@router.post("/admin/create-gallery")
async def create_gallery(folder_name: str, token: str):

    gallery_path = os.path.join(STORAGE_BASE, folder_name)
    os.makedirs(gallery_path, exist_ok=True)

    for sub in ["Wedding Images", "Video", "Guest Uploads", "Selfie Booth"]:
        os.makedirs(os.path.join(gallery_path, sub), exist_ok=True)

    gallery = await db.galleries.insert_one(
        gallery_document(folder_name, MAX_LIMIT, GUEST_LIMIT)
    )

    await db.share_links.insert_one(
        share_link_document(token, gallery.inserted_id, "read", "all")
    )

    return {"status": "gallery created successfully"}

@router.post("/admin/create-share-link")
async def create_share_link(
    folder_name: str,
    token: str,
    role: str,
    folder_scope: str = "all",
    password: str = None
):

    if role not in ["read", "edit", "full"]:
        raise HTTPException(status_code=400, detail="Invalid role")

    if folder_scope not in ["all", "guest_uploads_only"]:
        raise HTTPException(status_code=400, detail="Invalid folder scope")

    if password and len(password) < 5:
        raise HTTPException(status_code=400, detail="Password must be 5+ characters")

    existing_token = await db.share_links.find_one({"token": token})
    if existing_token:
        raise HTTPException(status_code=400, detail="Token already exists")

    gallery = await db.galleries.find_one({"folder_name": folder_name})
    if not gallery:
        raise HTTPException(status_code=404, detail="Gallery not found")

    password_hash = hash_password(password) if password else None

    await db.share_links.insert_one(
        share_link_document(token, gallery["_id"], role, folder_scope, password_hash)
    )

    return {"status": "share link created"}