import gspread
import time
from pathlib import Path
from datetime import datetime
from oauth2client.service_account import ServiceAccountCredentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload


def init_google_services(credentials_path, sheet_name):
    """
    Initialize Google Sheets and Drive services.
    
    Args:
        credentials_path: Path to your JSON credentials file
        sheet_name: Name of your Google Sheet
    
    Returns:
        Tuple of (sheet, drive_service)
    """
    scope = [
        'https://spreadsheets.google.com/feeds',
        'https://www.googleapis.com/auth/drive'
    ]
    
    creds = ServiceAccountCredentials.from_json_keyfile_name(credentials_path, scope)
    client = gspread.authorize(creds)
    drive_service = build('drive', 'v3', credentials=creds)
    sheet = client.open(sheet_name).sheet1
    
    #The sheet is for google sheets interface
    #The drive is for the google drive interface
    
    return sheet, drive_service


def upload_txt_to_drive(drive_service, file_path, folder_id=None):
    """
    Uploads a text file to Google Drive.
    
    Args:
        drive_service: The Google Drive service object
        file_path: Path to the .txt file you want to upload
        folder_id: (Optional) The ID of the Google Drive folder
    
    Returns:
        The file ID of the uploaded file
    """
    if isinstance(file_path, Path):
        file_path = str(file_path)
    # Get the filename from the path
    filename = file_path.split('\\')[-1].split('/')[-1]
    
    file_metadata = {
        'name': filename
    }
    
    if folder_id:
        file_metadata['parents'] = [folder_id]
    
    media = MediaFileUpload(file_path, mimetype='text/plain')
    
    file = drive_service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id',
        supportsAllDrives=True
    ).execute()
    
    print(f"File uploaded successfully. File ID: {file.get('id')}")
    return file.get('id')


def is_row_empty(row_num, sheet):
    return [] == sheet.row_values(row_num)

def get_row_vals(row_num, sheet):
    return sheet.row_values(row_num)     