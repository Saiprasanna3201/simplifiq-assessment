import os
from datetime import datetime
from google.oauth2 import service_account
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]


def get_sheets_service():
    creds = service_account.Credentials.from_service_account_file(
        "credentials.json", scopes=SCOPES
    )
    return build("sheets", "v4", credentials=creds)


def log_to_sheet(lead, pdf_path):
    """Append a new lead row to the Google Sheet."""
    sheet_id = os.getenv("GOOGLE_SHEET_ID")
    if not sheet_id:
        raise ValueError("GOOGLE_SHEET_ID not set in .env")

    service = get_sheets_service()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    row = [[
        now,
        lead.get("name", ""),
        lead.get("email", ""),
        lead.get("company", ""),
        lead.get("industry", ""),
        lead.get("website", ""),
        os.path.basename(pdf_path),
        "sent",
    ]]

    # Ensure header row exists on first use
    result = service.spreadsheets().values().get(
        spreadsheetId=sheet_id, range="Sheet1!A1:H1"
    ).execute()

    if not result.get("values"):
        header = [["Timestamp", "Name", "Email", "Company", "Industry",
                   "Website", "PDF File", "Status"]]
        service.spreadsheets().values().update(
            spreadsheetId=sheet_id,
            range="Sheet1!A1",
            valueInputOption="RAW",
            body={"values": header},
        ).execute()

    # Append data row
    service.spreadsheets().values().append(
        spreadsheetId=sheet_id,
        range="Sheet1!A:H",
        valueInputOption="RAW",
        insertDataOption="INSERT_ROWS",
        body={"values": row},
    ).execute()

    print(f"  Logged to Google Sheets: {lead['company']}")
