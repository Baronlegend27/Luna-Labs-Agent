from minio import Minio
import pandas as pd
import io
# --- CONFIGURATION ---
MINIO_ENDPOINT = "localhost:9000"  # change this if not local
ACCESS_KEY = "minioadmin"
SECRET_KEY = "minioadmin"
SECURE = False  # True if using https


client = Minio(
    MINIO_ENDPOINT,
    access_key=ACCESS_KEY,
    secret_key=SECRET_KEY,
    secure=SECURE
)

PATENT_STATUS = "Client 8760 - Luna Labs USA LLC) Patent Status Report (OCT2025).xlsx"
AWARDS = "awards_search_1760702903.csv"
CONTRACTS_AND_TECH = "Luna Labs Contracts and Technology Portfolio.xlsx"
CONTEXT_BUCKET = "contextdata"

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


def read_minio_file(bucket_name: str, object_name: str, client: Minio) -> pd.DataFrame:
    """
    Read a CSV or XLSX file directly from MinIO into a pandas DataFrame (in-memory only).

    Args:
        bucket_name (str): Name of the MinIO bucket
        object_name (str): Name/path of the file in the bucket
        client (Minio): An initialized Minio client

    Returns:
        pd.DataFrame: The file loaded into memory
    """
    response = client.get_object(bucket_name, object_name)
    try:
        # Read object bytes into memory
        file_bytes = response.read()

        # Choose how to parse based on file extension
        if object_name.lower().endswith(".csv"):
            df = pd.read_csv(io.BytesIO(file_bytes))
        elif object_name.lower().endswith((".xls", ".xlsx")):
            df = pd.read_excel(io.BytesIO(file_bytes))
        else:
            raise ValueError("Unsupported file type (use .csv or .xlsx)")

        return df

    finally:
        # Always close and release the connection
        response.close()
        response.release_conn()



if __name__ == "__main__":
    #list_files_in_bucket("contextdata")

    contracts_and_tech = read_minio_file(CONTEXT_BUCKET, CONTRACTS_AND_TECH, client)

    awards = read_minio_file(CONTEXT_BUCKET, AWARDS, client)

    patent_stat = read_minio_file(CONTEXT_BUCKET, PATENT_STATUS, client)

    print(contracts_and_tech[["ID", "Contract Number", "Phase", "Full Title", "Status", "Projected End Date"]])

    print(awards[["Award Title", "Phase", "Contract", "Contract End Date","Research Area Keywords"]])

    print(patent_stat[["Case Number","Patent Number", "Status", "Filing Date" ,"Expiration Date"]])


