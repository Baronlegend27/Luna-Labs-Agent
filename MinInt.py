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

if __name__ == "__main__":
    list_buckets()
