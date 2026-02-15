import os
from fastapi import APIRouter, HTTPException
from ..database import db
from ..config import STORAGE_BASE, MAX_LIMIT, GUEST_LIMIT
from ..models import gallery_document, share_link_document

router = APIRouter()

@router.post("/admin/create-gallery")
async def create_gallery(folder_name: str, token: str):

    gallery_path = os.path.join(STORAGE_BASE, folder_name)

    os.makedirs(gallery_path, exist_ok=True)

    subfolders = [
        "Wedding Images",
        "Video",
        "Guest Uploads",
        "Selfie Booth"
    ]

    for sub in subfolders:
        os.makedirs(os.path.join(gallery_path, sub), exist_ok=True)

    gallery = await db.galleries.insert_one(
        gallery_document(folder_name, MAX_LIMIT, GUEST_LIMIT)
    )

    await db.share_links.insert_one(
        share_link_document(
            token=token,
            gallery_id=gallery.inserted_id,
            role="read",
            folder_scope="all"
        )
    )

    return {"status": "gallery created successfully"}


@router.post("/admin/create-share-link")
async def create_share_link(
    folder_name: str,
    token: str,
    role: str,
    folder_scope: str = "all"
):

    if role not in ["read", "edit", "full"]:
        raise HTTPException(status_code=400, detail="Invalid role")

    if folder_scope not in ["all", "guest_uploads_only"]:
        raise HTTPException(status_code=400, detail="Invalid folder scope")

    existing_token = await db.share_links.find_one({"token": token})
    if existing_token:
        raise HTTPException(status_code=400, detail="Token already exists")

    gallery = await db.galleries.find_one({"folder_name": folder_name})
    if not gallery:
        raise HTTPException(status_code=404, detail="Gallery not found")

    await db.share_links.insert_one(
        share_link_document(
            token=token,
            gallery_id=gallery["_id"],
            role=role,
            folder_scope=folder_scope
        )
    )

    return {"status": "share link created"}