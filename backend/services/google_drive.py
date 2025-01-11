import sqlalchemy.orm as orm
import fastapi
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
import models
import schemas

# Define the scopes required for Google Drive access
SCOPES = ['https://www.googleapis.com/auth/drive']

def refresh_credentials(credentials: Credentials):
    """
    Refresh Google OAuth credentials if expired.
    """
    if credentials.expired and credentials.refresh_token:
        credentials.refresh(Request())
    return credentials


def save_google_drive_credentials(
    db: orm.Session,
    project_id: int,
    client_id: str,
    client_secret: str,
    token: str
):
    """
    Save or update Google Drive credentials for a project.
    """
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not project:
        raise fastapi.HTTPException(status_code=404, detail="Project not found.")
    
    google_drive = db.query(models.GoogleDrive).filter(
        models.GoogleDrive.project_id == project_id
    ).first()
    
    if not google_drive:
        google_drive = models.GoogleDrive(
            project_id=project_id,
            client_id=client_id,
            client_secret=client_secret,
            token=token
        )
        db.add(google_drive)
    else:
        google_drive.client_id = client_id
        google_drive.client_secret = client_secret
        google_drive.token = token
    
    db.commit()
    db.refresh(google_drive)
    return google_drive


def get_google_drive_credentials(db: orm.Session, project_id: int):
    """
    Retrieve Google Drive credentials for a project.
    """
    google_drive = db.query(models.GoogleDrive).filter(
        models.GoogleDrive.project_id == project_id
    ).first()
    if not google_drive:
        raise fastapi.HTTPException(
            status_code=404,
            detail="Google Drive integration not found for this project."
        )
    return google_drive


def list_files(db: orm.Session, project_id: int, page_token: str = None):
    """
    List files in Google Drive for a specific project.
    Supports pagination with a `page_token`.
    """
    google_drive = get_google_drive_credentials(db, project_id)
    credentials = Credentials(
        token=google_drive.token,
        client_id=google_drive.client_id,
        client_secret=google_drive.client_secret,
        scopes=SCOPES
    )
    credentials = refresh_credentials(credentials)
    service = build('drive', 'v3', credentials=credentials)
    results = service.files().list(
        pageSize=10,
        pageToken=page_token,
        fields="nextPageToken, files(id, name)"
    ).execute()
    files = results.get('files', [])
    next_page_token = results.get('nextPageToken')
    return {"files": files, "nextPageToken": next_page_token}


def navigate_folder(db: orm.Session, project_id: int, folder_id: str):
    """
    Navigate through a folder structure in Google Drive for a specific project.
    """
    google_drive = get_google_drive_credentials(db, project_id)
    credentials = Credentials(
        token=google_drive.token,
        client_id=google_drive.client_id,
        client_secret=google_drive.client_secret,
        scopes=SCOPES
    )
    credentials = refresh_credentials(credentials)
    service = build('drive', 'v3', credentials=credentials)
    try:
        results = service.files().list(
            q=f"'{folder_id}' in parents and trashed=false",
            pageSize=10,
            fields="files(id, name)"
        ).execute()
        files = results.get('files', [])
        return files
    except Exception as e:
        raise fastapi.HTTPException(status_code=400, detail=str(e))


def share_file(db: orm.Session, project_id: int, file_id: str):
    """
    Share a file or folder in Google Drive for a specific project and generate a shareable link.
    """
    google_drive = get_google_drive_credentials(db, project_id)
    credentials = Credentials(
        token=google_drive.token,
        client_id=google_drive.client_id,
        client_secret=google_drive.client_secret,
        scopes=SCOPES
    )
    credentials = refresh_credentials(credentials)
    service = build('drive', 'v3', credentials=credentials)
    permission = {
        'type': 'anyone',
        'role': 'reader'
    }
    try:
        service.permissions().create(fileId=file_id, body=permission).execute()
        file = service.files().get(fileId=file_id, fields="webViewLink").execute()
        return file.get("webViewLink")
    except Exception as e:
        raise fastapi.HTTPException(status_code=400, detail=str(e))


def find_file(db: orm.Session, project_id: int, file_name: str):
    """
    Find a specific file in Google Drive for a project and return its path.
    """
    google_drive = get_google_drive_credentials(db, project_id)
    credentials = Credentials(
        token=google_drive.token,
        client_id=google_drive.client_id,
        client_secret=google_drive.client_secret,
        scopes=SCOPES
    )
    credentials = refresh_credentials(credentials)
    service = build('drive', 'v3', credentials=credentials)
    results = service.files().list(
        q=f"name='{file_name}'",
        fields="files(id, name, parents)"
    ).execute()
    files = results.get('files', [])
    if not files:
        return f"No file found with name '{file_name}'."
    return files