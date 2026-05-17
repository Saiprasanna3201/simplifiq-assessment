import os
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

SCOPES = ["https://www.googleapis.com/auth/drive.file"]


def get_drive_service():
    creds = service_account.Credentials.from_service_account_file(
        "credentials.json", scopes=SCOPES
    )
    return build("drive", "v3", credentials=creds)


def upload_to_drive(pdf_path):
    """Upload the PDF to the configured Google Drive folder."""
    folder_id = os.getenv("GOOGLE_DRIVE_FOLDER_ID")
    if not folder_id:
        raise ValueError("GOOGLE_DRIVE_FOLDER_ID not set in .env")

    service = get_drive_service()
    filename = os.path.basename(pdf_path)

    file_metadata = {
        "name": filename,
        "parents": [folder_id],
    }
    media = MediaFileUpload(pdf_path, mimetype="application/pdf", resumable=True)

    uploaded = service.files().create(
        body=file_metadata,
        media_body=media,
        fields="id, name, webViewLink",
    ).execute()

    print(f"  Uploaded to Drive: {uploaded.get('webViewLink', 'unknown link')}")
    return uploaded
