from datetime import datetime

def gallery_document(folder_name: str, storage_limit: int, guest_limit: int):
    return {
        "folder_name": folder_name,
        "storage_limit": storage_limit,
        "guest_limit": guest_limit,
        "created_at": datetime.utcnow()
    }

def share_link_document(token: str, gallery_id, role: str, folder_scope: str, password_hash=None):
    return {
        "token": token,
        "gallery_id": gallery_id,
        "role": role,
        "folder_scope": folder_scope,
        "password_hash": password_hash,
        "created_at": datetime.utcnow()
    }