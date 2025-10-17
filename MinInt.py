from minio import Minio

# --- CONFIGURATION ---
MINIO_ENDPOINT = "localhost:9000"  # change this if not local
ACCESS_KEY = "minioadmin"
SECRET_KEY = "minioadmin"
SECURE = False  # True if using https

def list_buckets():
    """Print all available buckets in your MinIO server."""
    client = Minio(
        MINIO_ENDPOINT,
        access_key=ACCESS_KEY,
        secret_key=SECRET_KEY,
        secure=SECURE
    )

    buckets = client.list_buckets()
    if not buckets:
        print("No buckets found.")
    else:
        print("Buckets:")
        for bucket in buckets:
            print(f" - {bucket.name}")

def list_files_in_bucket(bucket_name):
    """Print all file names in the given bucket."""
    client = Minio(
        MINIO_ENDPOINT,
        access_key=ACCESS_KEY,
        secret_key=SECRET_KEY,
        secure=SECURE
    )

    try:
        objects = client.list_objects(bucket_name)
        print(f"Files in bucket '{bucket_name}':")
        empty = True
        for obj in objects:
            print(f" - {obj.object_name}")
            empty = False
        if empty:
            print(" (No files found in this bucket.)")
    except Exception as e:
        print(f"Error listing files in bucket '{bucket_name}': {e}")


if __name__ == "__main__":
    list_buckets()
