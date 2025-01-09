import fastapi
import sqlalchemy.orm as orm
import fastapi.security as security
from starlette.responses import JSONResponse
from typing import List

from services import users as services_users, projects as services_projects
import schemas
import database

router = fastapi.APIRouter()


@router.post("/api/projects", response_model=schemas.Project)
async def create_project(
    project: schemas.ProjectCreate,
    user: schemas.User = fastapi.Depends(services_users.get_current_user),
    db: orm.Session = fastapi.Depends(database.get_db),
):
    return await services_projects.create_project(user=user, db=db, project=project)


@router.get("/api/projects", response_model=List[schemas.Project])
async def get_projects(
    user: schemas.User = fastapi.Depends(services_users.get_current_user),
    db: orm.Session = fastapi.Depends(database.get_db),
):
    return await services_projects.get_projects(user=user, db=db)


@router.get("/api/projects/{project_id}", status_code=200)
async def get_project(
    project_id: int,
    user: schemas.User = fastapi.Depends(services_users.get_current_user),
    db: orm.Session = fastapi.Depends(database.get_db),
):
    return await services_projects.get_project(project_id, user, db)


@router.delete("/api/projects/{project_id}", status_code=204)
async def delete_project(
    project_id: int,
    user: schemas.User = fastapi.Depends(services_users.get_current_user),
    db: orm.Session = fastapi.Depends(database.get_db),
):
    await services_projects.delete_project(project_id, user, db)
    return {"message", "Successfully Deleted"}


@router.put("/api/projects/{project_id}", status_code=200)
async def update_project(
    project_id: int,
    project: schemas.ProjectCreate,
    user: schemas.User = fastapi.Depends(services_users.get_current_user),
    db: orm.Session = fastapi.Depends(database.get_db),
):
    await services_projects.update_project(project_id, project, user, db)
    return {"message", "Successfully Updated"}


