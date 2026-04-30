import os
from google.cloud import storage
from typing import Optional

def get_storage_client():
    """Initializes the GCS client."""
    return storage.Client()

def persist_file(local_path: str, bucket_name: str, remote_path: str):
    """Persists a local file to GCS."""
    client = get_storage_client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(remote_path)
    blob.upload_from_filename(local_path)

def fetch_file(bucket_name: str, remote_path: str, local_path: str):
    """Fetches a file from GCS."""
    client = get_storage_client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(remote_path)
    blob.download_to_filename(local_path)
