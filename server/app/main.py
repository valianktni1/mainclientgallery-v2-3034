from fastapi import FastAPI
from .routes import galleries, uploads, downloads

app = FastAPI(title="Main Client Gallery")

app.include_router(galleries.router)
app.include_router(uploads.router)
app.include_router(downloads.router)