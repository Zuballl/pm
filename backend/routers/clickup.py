import fastapi
import sqlalchemy.orm as orm

from services import users as services_users, clickup as services_clickup
import schemas
import database

router = fastapi.APIRouter()

@router.post("/api/clickup/token")
def add_clickup_token(
    token: schemas.ClickUpTokenCreate,
    db: orm.Session = fastapi.Depends(database.get_db),
    user=fastapi.Depends(services_users.get_current_user),
):
    services_clickup.save_clickup_token(db, user.id, token.api_token)
    return {"message": "ClickUp API token saved successfully"}


@router.post("/api/projects/{project_id}/clickup-list")
def associate_clickup_list(
    project_id: int,
    list_id: str,
    db: orm.Session = fastapi.Depends(database.get_db),
    user=fastapi.Depends(services_users.get_current_user),
):
    services_clickup.associate_list_with_project(db, user.id, project_id, list_id)
    return {"message": f"ClickUp list {list_id} associated with project {project_id}"}