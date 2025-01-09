import fastapi
import sqlalchemy.orm as orm
import typing
import datetime as dt


import models
import schemas


async def create_project(user: schemas.User, db: orm.Session, project: schemas.ProjectCreate):
    project = models.Project(**project.dict(), owner_id=user.id)
    db.add(project)
    db.commit()
    db.refresh(project)
    return schemas.Project.from_orm(project)


async def get_projects(user: schemas.User, db: orm.Session):
    projects = db.query(models.Project).filter_by(owner_id=user.id)

    return list(map(schemas.Project.from_orm, projects))


async def project_selector(project_id: int, user: schemas.User, db: orm.Session):
    project = (
        db.query(models.Project)
        .filter_by(owner_id=user.id)
        .filter(models.Project.id == project_id)
        .first()
    )

    if project is None:
        raise fastapi.HTTPException(status_code=404, detail="Project does not exist")

    return project


async def get_project(project_id: int, user: schemas.User, db: orm.Session):
    project = await project_selector(project_id=project_id, user=user, db=db)

    return schemas.Project.from_orm(project)


async def delete_project(project_id: int, user: schemas.User, db: orm.Session):
    project = await project_selector(project_id, user, db)

    db.delete(project)
    db.commit()

async def update_project(project_id: int, project: schemas.ProjectCreate, user: schemas.User, db: orm.Session):
    project_db = await project_selector(project_id, user, db)

    project_db.name = project.name
    project_db.department = project.department
    project_db.client = project.client
    project_db.deadline = project.deadline
    project_db.description = project.description
    project_db.date_last_updated = dt.datetime.utcnow()

    db.commit()
    db.refresh(project_db)

    return schemas.Project.from_orm(project_db)







