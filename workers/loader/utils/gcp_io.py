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
