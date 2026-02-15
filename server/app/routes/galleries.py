import os
from fastapi import APIRouter, HTTPException
from ..database import db
from ..config import STORAGE_BASE, MAX_LIMIT, GUEST_LIMIT
from ..models import gallery_document, share_link_document

router = APIRouter()

@router.post("/admin/create-gallery")
async def create_gallery(folder_name: str, token: str):
    gallery_path = os.path.join(STORAGE_BASE, folder_name)
    if not os.path.exists(gallery_path):
        raise HTTPException(status_code=400, detail="Folder does not exist")

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

    return {"status": "gallery created with default read link"}