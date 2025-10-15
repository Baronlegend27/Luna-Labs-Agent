from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import io
import os
import pdfplumber
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials


SERVICE_ACCOUNT_PATH = "C:\\Users\\Baron\\Downloads\\modern-venture-474620-a8-f4fa5868355c.json"
OUTPUT_FOLDER = "C:\\Users\\Baron\\Documents\\Luna Labs Agent\\TextFiles"
TEMPLATE_FILE = "C:\\Users\\Baron\\Documents\\Luna Labs Agent\SupportFiles\prompt_outline.txt"


link = "https://drive.google.com/open?id=1XOGW5EBVA5CgAEA4CbBJfql8vrLio3Aq"


def txt_file_exists(link_id, json_file_path=TEMPLATE_FILE):
    """
    Check if a JSON file contains the given key at the top level.
    
    Args:
        json_file_path (str): Path to the JSON file.
        key_to_check (str): Key to look for.
        
    Returns:
        bool: True if key exists, False otherwise.
    """
    try:
        with open(json_file_path, "r") as f:
            data = json.load(f)
        
        return link_id in data
        
    except Exception as e:
        print(f"Error reading JSON file: {e}")
        return False

def update_lookup(link_id, text_file_id, json_file_path=TEMPLATE_FILE):
    """Add or update the link_id -> text_file_id mapping."""
    try:
        # Load existing data
        if os.path.exists(json_file_path):
            with open(json_file_path, "r") as f:
                data = json.load(f)
        else:
            data = {}
        
        # Add new mapping
        data[link_id] = text_file_id
        
        # Save back
        with open(json_file_path, "w") as f:
            json.dump(data, f, indent=2)
            
    except Exception as e:
        print(f"Error updating lookup: {e}")

def get_link_id(link):
    if "id=" in link:
        return link.split("id=")[1].split("&")[0]
    return None

def generate_txt_id(link_id):
    """
    Given a Google Drive file ID, generate a stable numeric ID string.
    """
    n = 0
    for c in link_id:
        n = (n * 37 + ord(c)) % 1000000000  # keep it within 9 digits
    return str(n).zfill(8)


def setup_google_services(service_account_path: str):
    """
    Sets up Google Sheets and Drive services using a shared OAuth2 credential.
    """
    scopes = [
        'https://spreadsheets.google.com/feeds',
        'https://www.googleapis.com/auth/drive'
    ]

    creds = ServiceAccountCredentials.from_json_keyfile_name(service_account_path, scopes)
    client = gspread.authorize(creds)
    drive_service = build('drive', 'v3', credentials=creds)

    return client, drive_service


def get_pdf_bytes_from_drive(file_id: str, drive_service) -> bytes:
    request = drive_service.files().get_media(fileId=file_id)
    buffer = io.BytesIO()
    downloader = MediaIoBaseDownload(buffer, request)

    done = False
    while not done:
        _, done = downloader.next_chunk()

    buffer.seek(0)
    return buffer.read()


def extract_text_from_pdf_bytes(pdf_bytes: bytes) -> str:
    text = []
    with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
        for page in pdf.pages:
            content = page.extract_text()
            if content:
                text.append(content)
    return "\n".join(text).strip()


def save_text_locally(file_id: str, text: str, output_folder: str) -> str:
    os.makedirs(output_folder, exist_ok=True)
    txt_filename = f"{file_id}.txt"
    output_path = os.path.join(output_folder, txt_filename)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(text)

    print(f"✅ Saved text file to: {output_path}")
    return output_path


def pdf_to_txt(pdf_link):
    """
    Convert a Google Drive PDF to text file.
    
    Returns:
        str: Text file ID if successful, existing ID if already processed, None if error
    """
    client, drive_service = setup_google_services(SERVICE_ACCOUNT_PATH)

    link_id = get_link_id(pdf_link)
    
    if not link_id:
        print("❌ Invalid link - couldn't extract file ID")
        return None

    # Check if already processed
    if txt_file_exists(link_id):
        print(f"✅ Text file already exists for {link_id}")
        # Optionally load and return the existing text_file_id from lookup.json
        with open("lookup.json", "r") as f:
            data = json.load(f)
        return data[link_id]
    
    # Generate new ID for text file
    text_file_id = generate_txt_id(link_id)

    try:
        # Download PDF from Drive using the ORIGINAL link_id
        pdf_bytes = get_pdf_bytes_from_drive(link_id, drive_service)

        # Extract text
        pdf_text = extract_text_from_pdf_bytes(pdf_bytes)

        # Save locally using the GENERATED text_file_id
        save_text_locally(text_file_id, pdf_text, OUTPUT_FOLDER)

        # Update lookup so we know it's been processed
        update_lookup(link_id, text_file_id)
        
        return text_file_id
        
    except Exception as e:
        print(f"❌ Error processing PDF: {e}")
        return None
    
pdf_to_txt(link)