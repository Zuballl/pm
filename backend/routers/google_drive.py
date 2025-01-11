from fastapi import APIRouter, Depends, HTTPException
import sqlalchemy.orm as orm
from database import get_db
from schemas import GoogleDriveCreate
from services import google_drive as google_drive_service

router = APIRouter(prefix="/api/projects/{project_id}/google-drive")

@router.post("/config")
def configure_google_drive(
    project_id: int,
    data: GoogleDriveCreate,
    db: orm.Session = Depends(get_db)
):
    """
    Configure Google Drive integration for a project by saving credentials.
    """
    try:
        google_drive = google_drive_service.save_google_drive_credentials(
            db=db,
            project_id=project_id,
            client_id=data.client_id,
            client_secret=data.client_secret,
            token=data.token
        )
        return {"message": "Google Drive configuration saved successfully.", "data": google_drive}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/files")
def list_google_drive_files(
    project_id: int,
    page_token: str = None,
    db: orm.Session = Depends(get_db)
):
    """
    List files in Google Drive for a specific project.
    """
    try:
        files_data = google_drive_service.list_files(db=db, project_id=project_id, page_token=page_token)
        return files_data
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/folders/{folder_id}")
def navigate_google_drive_folder(
    project_id: int,
    folder_id: str,
    db: orm.Session = Depends(get_db)
):
    """
    Navigate through a folder in Google Drive for a specific project.
    """
    try:
        files = google_drive_service.navigate_folder(db=db, project_id=project_id, folder_id=folder_id)
        return {"files": files}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/share/{file_id}")
def share_google_drive_file(
    project_id: int,
    file_id: str,
    db: orm.Session = Depends(get_db)
):
    """
    Share a Google Drive file and generate a shareable link.
    """
    try:
        link = google_drive_service.share_file(db=db, project_id=project_id, file_id=file_id)
        return {"shareable_link": link}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/find")
def find_google_drive_file(
    project_id: int,
    file_name: str,
    db: orm.Session = Depends(get_db)
):
    """
    Find a specific file in Google Drive for a project.
    """
    try:
        files = google_drive_service.find_file(db=db, project_id=project_id, file_name=file_name)
        return {"files": files}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))