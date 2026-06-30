import os
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

from config.google.auth import get_google_credentials

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")


def _get_drive_service():
    creds = get_google_credentials()
    return build("drive", "v3", credentials=creds)


def _safe_data_path(filename: str) -> str:
    path = os.path.abspath(os.path.join(DATA_DIR, filename))
    if not path.startswith(os.path.abspath(DATA_DIR)):
        raise ValueError("Access outside data/ directory is not allowed.")
    return path


def upload_file_to_drive(filename: str, drive_folder_id: str = None) -> str:
    """
    Uploads a file from the local data/ folder to Google Drive.
    Uses 'drive.file' scope, so the agent can only see/manage files it creates.
    """
    local_path = _safe_data_path(filename)

    if not os.path.exists(local_path):
        return f"Error: local file '{filename}' not found in data folder."

    service = _get_drive_service()

    file_metadata = {"name": filename}
    if drive_folder_id:
        file_metadata["parents"] = [drive_folder_id]

    media = MediaFileUpload(local_path, resumable=True)

    uploaded = (
        service.files()
        .create(body=file_metadata, media_body=media, fields="id, name, webViewLink")
        .execute()
    )

    return (
        f"Uploaded '{uploaded['name']}' to Google Drive. "
        f"File ID: {uploaded['id']}. Link: {uploaded.get('webViewLink', 'N/A')}"
    )