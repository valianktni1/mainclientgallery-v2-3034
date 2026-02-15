import os

MONGO_URL = os.getenv("MONGO_URL")
DB_NAME = os.getenv("DB_NAME")

STORAGE_BASE = "/app/storage"

MAX_LIMIT = 40 * 1024 * 1024 * 1024
GUEST_LIMIT = 1 * 1024 * 1024 * 1024

JWT_SECRET = "supersecretkey"
JWT_EXPIRE_HOURS = 12