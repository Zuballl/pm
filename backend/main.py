from typing import List
import fastapi as _fastapi
import fastapi.security as _security
import sqlalchemy.orm as _orm
from starlette.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware


import services as _services
import schemas as _schemas
import database as _database


app = _fastapi.FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/api/users")
async def create_user(
    user: _schemas.UserCreate, db: _orm.Session = _fastapi.Depends(_services.get_db)
):
    db_user = await _services.get_user_by_username(user.username, db)
    if db_user:
        raise _fastapi.HTTPException(status_code=400, detail="Username already exists")

    new_user = await _services.create_user(user, db)

    # Generate token for the new user
    token = await _services.create_token(new_user)

    return token



@app.post("/api/token")
async def generate_token(
    form_data: _security.OAuth2PasswordRequestForm = _fastapi.Depends(),
    db: _orm.Session = _fastapi.Depends(_services.get_db),
):
    user = await _services.authenticate_user(form_data.username, form_data.password, db)

    if not user:
        raise _fastapi.HTTPException(status_code=401, detail="Invalid Credentials")

    return await _services.create_token(user)


@app.get("/api/users/me", response_model=_schemas.User)
async def get_user(user: _schemas.User = _fastapi.Depends(_services.get_current_user)):
    return user



@app.post("/api/projects", response_model=_schemas.Project)
async def create_project(
    project: _schemas.ProjectCreate,
    user: _schemas.User = _fastapi.Depends(_services.get_current_user),
    db: _orm.Session = _fastapi.Depends(_services.get_db),
):
    return await _services.create_project(user=user, db=db, project=project)


@app.get("/api/projects", response_model=List[_schemas.Project])
async def get_projects(
    user: _schemas.User = _fastapi.Depends(_services.get_current_user),
    db: _orm.Session = _fastapi.Depends(_services.get_db),
):
    return await _services.get_projects(user=user, db=db)


@app.get("/api/projects/{project_id}", status_code=200)
async def get_project(
    project_id: int,
    user: _schemas.User = _fastapi.Depends(_services.get_current_user),
    db: _orm.Session = _fastapi.Depends(_services.get_db),
):
    return await _services.get_project(project_id, user, db)


@app.delete("/api/projects/{project_id}", status_code=204)
async def delete_project(
    project_id: int,
    user: _schemas.User = _fastapi.Depends(_services.get_current_user),
    db: _orm.Session = _fastapi.Depends(_services.get_db),
):
    await _services.delete_project(project_id, user, db)
    return {"message", "Successfully Deleted"}


@app.put("/api/projects/{project_id}", status_code=200)
async def update_project(
    project_id: int,
    project: _schemas.ProjectCreate,
    user: _schemas.User = _fastapi.Depends(_services.get_current_user),
    db: _orm.Session = _fastapi.Depends(_services.get_db),
):
    await _services.update_project(project_id, project, user, db)
    return {"message", "Successfully Updated"}


@app.get("/api")
async def root():
    return {"message": "Awesome Projects Manager"}




@app.post("/api/gpt-query", response_model=_schemas.GPTQueryResponse)
async def gpt_query(
    request: _schemas.GPTQueryRequest,     
    user: _schemas.User = _fastapi.Depends(_services.get_current_user),
    db: _orm.Session = _fastapi.Depends(_services.get_db)
):


    try:
        # Fetch project context if project_id is provided
        project_context = None
        if request.project_id:
            project_context = await _services.get_project_context(db, request.project_id, user.id)

        # Call the GPT service to get the response
        gpt_response = await _services.get_gpt_response(db, request.query, user.id, request.project_id, project_context)
        return _schemas.GPTQueryResponse(response=gpt_response)
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})



@app.post("/api/save-chat", response_model=_schemas.ChatResponse)
async def save_chat_endpoint(
    chat_request: _schemas.ChatCreateRequest,
    db: _orm.Session = _fastapi.Depends(_services.get_db),
    current_user = _fastapi.Depends(_services.get_current_user)
):
    chat = _services.save_chat(
        db=db,
        user_id=current_user.id,
        query=chat_request.query,
        response=chat_request.response,
        project_id=chat_request.project_id,
    )
    return chat



@app.get("/api/get-chats", response_model=_schemas.ChatListResponse)
async def get_chats_endpoint(
    db: _orm.Session = _fastapi.Depends(_services.get_db),
    current_user = _fastapi.Depends(_services.get_current_user)
):
    chats = _services.get_chats(db, user_id=current_user.id)
    return {"chats": chats}