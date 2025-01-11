import fastapi
import sqlalchemy.orm as orm

import schemas
import models
import database
from services import clickup as services_clickup, users as services_users

router = fastapi.APIRouter()

@router.post("/api/projects/{project_id}/clickup")
def connect_project_to_clickup(
    project_id: int,
    data: schemas.ClickUpConnect,
    db: orm.Session = fastapi.Depends(database.get_db),
    current_user: models.User = fastapi.Depends(services_users.get_current_user),
):

    services_clickup.connect_project_to_clickup(
        db=db, 
        project_id=project_id, 
        user=current_user, 
        api_token=data.api_token, 
        list_id=data.list_id
    )
    return {"message": f"Project {project_id} successfully connected to ClickUp"}