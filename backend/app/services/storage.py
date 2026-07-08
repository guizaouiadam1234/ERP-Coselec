import os
from minio import Minio

BUCKET_NAME = "coselec-hr-documents"


def get_minio_client() -> Minio:
    endpoint = os.getenv("MINIO_ENDPOINT")
    if not endpoint:
        raise RuntimeError(
            "MINIO_ENDPOINT is not configured. Set it before uploading documents."
        )

    return Minio(
        endpoint,
        access_key=os.getenv("MINIO_ACCESS_KEY", "minioadmin"),
        secret_key=os.getenv("MINIO_SECRET_KEY", "minioadmin"),
        secure=False,
    )

def upload_file_to_minio(file, file_name):
    minio_client = get_minio_client()

    if not minio_client.bucket_exists(BUCKET_NAME):
        minio_client.make_bucket(BUCKET_NAME)
    
    file.file.seek(0, 2)
    file_size = file.file.tell()
    file.file.seek(0)
    
    minio_client.put_object(
        BUCKET_NAME,
        file_name,
        file.file, 
        length=file_size,
        part_size=10*1024*1024,
        content_type=file.content_type
    )
    return f"{BUCKET_NAME}/{file_name}"

def save_file_locally(file, file_name):
    local_path = os.path.join("uploads", file_name)
    os.makedirs(os.path.dirname(local_path), exist_ok=True)
    
    with open(local_path, "wb") as f:
        f.write(file.file.read())
    
    return local_path