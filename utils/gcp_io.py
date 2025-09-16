# utils/gcp_io.py
from google.cloud import storage
from google.api_core.exceptions import Conflict

def get_storage_client():
    return storage.Client()

def ensure_bucket(bucket_name: str, location: str="EU"):
    client = get_storage_client()
    try:
        client.create_bucket(bucket_name, location=location)
    except Conflict:
        pass
    return bucket_name

def upload_fileobj(bucket_name: str, blob_path: str, fileobj):
    client = get_storage_client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(blob_path)
    fileobj.seek(0)
    blob.upload_from_file(fileobj, rewind=True, content_type="text/csv")
    return f"gs://{bucket_name}/{blob_path}"
