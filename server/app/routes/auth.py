from fastapi import APIRouter, HTTPException
from datetime import datetime, timedelta
from ..database import db
from ..security import verify_password, create_session_token

router = APIRouter()

@router.post("/auth/{token}")
async def authenticate(token: str, password: str):
    link = await db.share_links.find_one({"token": token})
    if not link:
        raise HTTPException(status_code=404, detail="Invalid link")

    if not link.get("password_hash"):
        return {"status": "no password required"}

    if link.get("locked_until") and link["locked_until"] > datetime.utcnow():
        raise HTTPException(status_code=403, detail="Link locked. Try later.")

    if not verify_password(password, link["password_hash"]):
        failed = link.get("failed_attempts", 0) + 1
        update = {"failed_attempts": failed}
        if failed >= 3:
            update["locked_until"] = datetime.utcnow() + timedelta(hours=1)
            update["failed_attempts"] = 0
        await db.share_links.update_one({"_id": link["_id"]}, {"$set": update})
        raise HTTPException(status_code=403, detail="Incorrect password")

    await db.share_links.update_one(
        {"_id": link["_id"]},
        {"$set": {"failed_attempts": 0, "locked_until": None}}
    )

    session = create_session_token(token)
    return {"session_token": session}