import fastapi as _fastapi
import fastapi.security as _security
import jwt as _jwt
import datetime as _dt
import sqlalchemy.orm as _orm
import passlib.hash as _hash
from openai import OpenAI
import os
from fastapi import HTTPException
import typing as _typing


import database as _database
import models as _models
import schemas as _schemas


oauth2schema = _security.OAuth2PasswordBearer(tokenUrl="/api/token")

JWT_SECRET = "myjwtsecret"

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))



def create_database():
    return _database.Base.metadata.create_all(bind=_database.engine)


def get_db():
    db = _database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_user_by_username(username: str, db: _orm.Session):
    return db.query(_models.User).filter(_models.User.username == username).first()


async def create_user(user: _schemas.UserCreate, db: _orm.Session):
    user_obj = _models.User(
        username=user.username, hashed_password=_hash.bcrypt.hash(user.hashed_password)
    )
    db.add(user_obj)
    db.commit()
    db.refresh(user_obj)
    return user_obj


async def authenticate_user(username: str, password: str, db: _orm.Session):
    user = await get_user_by_username(db=db, username=username)

    if not user:
        return False

    if not user.verify_password(password):
        return False

    return user


async def create_token(user: _models.User):
    user_obj = _schemas.User.from_orm(user)

    token = _jwt.encode(user_obj.dict(), JWT_SECRET)

    return dict(access_token=token, token_type="bearer")


async def get_current_user(
    db: _orm.Session = _fastapi.Depends(get_db),
    token: str = _fastapi.Depends(oauth2schema),
):
    try:
        payload = _jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        user = db.query(_models.User).get(payload["id"])
    except:
        raise _fastapi.HTTPException(
            status_code=401, detail="Invalid Email or Password"
        )

    return _schemas.User.from_orm(user)


async def create_project(user: _schemas.User, db: _orm.Session, project: _schemas.ProjectCreate):
    project = _models.Project(**project.dict(), owner_id=user.id)
    db.add(project)
    db.commit()
    db.refresh(project)
    return _schemas.Project.from_orm(project)


async def get_projects(user: _schemas.User, db: _orm.Session):
    projects = db.query(_models.Project).filter_by(owner_id=user.id)

    return list(map(_schemas.Project.from_orm, projects))


async def _project_selector(project_id: int, user: _schemas.User, db: _orm.Session):
    project = (
        db.query(_models.Project)
        .filter_by(owner_id=user.id)
        .filter(_models.Project.id == project_id)
        .first()
    )

    if project is None:
        raise _fastapi.HTTPException(status_code=404, detail="Project does not exist")

    return project


async def get_project(project_id: int, user: _schemas.User, db: _orm.Session):
    project = await _project_selector(project_id=project_id, user=user, db=db)

    return _schemas.Project.from_orm(project)


async def delete_project(project_id: int, user: _schemas.User, db: _orm.Session):
    project = await _project_selector(project_id, user, db)

    db.delete(project)
    db.commit()

async def update_project(project_id: int, project: _schemas.ProjectCreate, user: _schemas.User, db: _orm.Session):
    project_db = await _project_selector(project_id, user, db)

    project_db.name = project.name
    project_db.department = project.department
    project_db.client = project.client
    project_db.deadline = project.deadline
    project_db.description = project.description
    project_db.date_last_updated = _dt.datetime.utcnow()

    db.commit()
    db.refresh(project_db)

    return _schemas.Project.from_orm(project_db)













async def get_project_context(db: _orm.Session, project_id: int, user_id: int):
    """
    Fetch project details for a given project_id from the database.
    """
    project = db.query(_models.Project).filter(
        _models.Project.id == project_id, 
        _models.Project.owner_id == user_id  
    ).first()

    if not project:
        raise HTTPException(status_code=404, detail="Project is not found or you are not authorised to access it.")
    return {
        "Project Name": project.name,
        "Department": project.department,
        "Client": project.client,
        "Deadline": project.deadline,
        "Description": project.description,

    }





async def get_gpt_response(
    db: _orm.Session, query: str, user_id: int, project_id: _typing.Optional[int] = None, project_context: dict = None
) -> str:

    try:
        # Prepare the input message
        system_message = (
            f"Context: {project_context}" if project_context else "General Query"
        )
        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": query},
        ]

        # Call the GPT API
        response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=0.7
        )

        # Extract and return the GPT response
        gpt_response = response.choices[0].message.content


        save_chat(db, user_id=user_id, query=query, response=gpt_response, project_id=project_id)
        
        return gpt_response


    except Exception as e:
        raise Exception(f"Error querying GPT: {str(e)}")
    



def save_chat(
    db: _orm.Session, user_id: int, query: str, response: str, project_id: _typing.Optional[int] = None
):
    new_chat = _models.ChatHistory(
        user_id=user_id, query=query, response=response, project_id=project_id
    )
    db.add(new_chat)
    db.commit()
    db.refresh(new_chat)
    return new_chat

def get_chats(db: _orm.Session, user_id: int):
    return db.query(_models.ChatHistory).filter(_models.ChatHistory.user_id == user_id).all()



