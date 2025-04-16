import random
import string
from app.core.s3.minio_client import upload_files_to_minio
from app.core.schemas.user import UserCreate
from app.core.database.pocketbase_client import pb


def generate_id(length=11):
    """Generate a random ID with default length of 11 characters"""
    chars = string.ascii_lowercase + string.digits
    return ''.join(random.choice(chars) for _ in range(length))


def handle_user_create(data: UserCreate, files, tenant_id: str):
    # Upload files to MinIO
    user_id = generate_id()  # This will now generate an 11-char ID
    bucket_name = f"{user_id}_us"
    image_urls = upload_files_to_minio(bucket_name, tenant_id, files)

    # Save to PB
    payload = data.dict()
    payload["id"] = user_id
    payload["images"] = image_urls
    pb.collection("vms_i61b74n38e_users").create(payload)
    return {"id": user_id, "images": image_urls}
