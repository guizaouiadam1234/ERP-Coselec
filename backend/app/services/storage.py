from minio import Minio
import os

minio_client = Minio(
    os.getenv("MINIO_ENDPOINT"),
    access_key=os.getenv("MINIO_ACCESS_KEY", "minioadmin"),
    secret_key=os.getenv("MINIO_SECRET_KEY", "minioadmin"),
    secure=False
)

BUCKET_NAME = "coselec-hr-documents"

def upload_file_to_minio(file, file_name):
    if not minio_client.bucket_exists(BUCKET_NAME):
        minio_client.make_bucket(BUCKET_NAME)
    minio.client.put_object(
        BUCKET_NAME,
        file_name,
        file_data,
        length=1,
        part_size=10*1024*1024,
        content_type=file.content_type
    )
    return f"{BUCKET_NAME}/{file_name}"

