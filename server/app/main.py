from fastapi import FastAPI
from .routes import galleries, uploads, downloads, auth

app = FastAPI(title="Main Client Gallery")

app.include_router(galleries.router)
app.include_router(auth.router)
app.include_router(uploads.router)
app.include_router(downloads.router)