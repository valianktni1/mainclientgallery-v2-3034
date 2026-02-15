
import os
import shutil
from fastapi import FastAPI, UploadFile, HTTPException
from fastapi.responses import FileResponse
from motor.motor_asyncio import AsyncIOMotorClient

MAX_LIMIT = 40 * 1024 * 1024 * 1024  # 40GB
GUEST_LIMIT = 1 * 1024 * 1024 * 1024  # 1GB

app = FastAPI(title="Main Client Gallery")

mongo_url = os.getenv("MONGO_URL")
db_name = os.getenv("DB_NAME")

client = AsyncIOMotorClient(mongo_url)
db = client[db_name]

STORAGE_BASE = "/app/storage"

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

@app.post("/admin/create-gallery")
async def create_gallery(token: str, folder_name: str):
    existing = await db.galleries.find_one({"token": token})
    if existing:
        raise HTTPException(status_code=400, detail="Token exists")

    gallery_path = os.path.join(STORAGE_BASE, folder_name)
    if not os.path.exists(gallery_path):
        raise HTTPException(status_code=400, detail="Folder does not exist")

    await db.galleries.insert_one({
        "token": token,
        "folder_name": folder_name,
        "storage_limit": MAX_LIMIT,
        "guest_limit": GUEST_LIMIT,
        "upload_enabled": True
    })

    return {"status": "gallery linked"}

@app.post("/upload/{token}")
async def upload_file(token: str, file: UploadFile):
    gallery = await db.galleries.find_one({"token": token})
    if not gallery:
        raise HTTPException(status_code=404, detail="Gallery not found")

    gallery_path = os.path.join(STORAGE_BASE, gallery["folder_name"])

    safe_filename = safe_name(file.filename)

    if file.content_type.startswith("video"):
        subfolder = "Video"
    else:
        subfolder = "Wedding Images"

    dest_dir = os.path.join(gallery_path, subfolder)
    dest_path = rename_if_exists(os.path.join(dest_dir, safe_filename))

    written = 0

    with open(dest_path, "wb") as buffer:
        while chunk := await file.read(10 * 1024 * 1024):
            written += len(chunk)

            total_size = sum(
                os.path.getsize(os.path.join(dp, f))
                for dp, dn, filenames in os.walk(gallery_path)
                for f in filenames
            )

            if total_size > gallery["storage_limit"]:
                buffer.close()
                os.remove(dest_path)
                raise HTTPException(status_code=400, detail="40GB limit reached")

            buffer.write(chunk)

    return {"status": "uploaded"}

@app.get("/download/video/{token}/{filename}")
async def download_video(token: str, filename: str):
    gallery = await db.galleries.find_one({"token": token})
    if not gallery:
        raise HTTPException(status_code=404, detail="Gallery not found")

    path = os.path.join(STORAGE_BASE, gallery["folder_name"], "Video", filename)
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(path, media_type="video/mp4")

@app.get("/download/images-zip/{token}")
async def download_images_zip(token: str):
    gallery = await db.galleries.find_one({"token": token})
    if not gallery:
        raise HTTPException(status_code=404, detail="Gallery not found")

    base = os.path.join(STORAGE_BASE, gallery["folder_name"])
    images_folder = os.path.join(base, "Wedding Images")
    zip_path = os.path.join(base, "generated_full_images")

    shutil.make_archive(zip_path, 'zip', images_folder)

    return FileResponse(zip_path + ".zip", media_type="application/zip")
