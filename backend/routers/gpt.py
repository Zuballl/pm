import fastapi
import sqlalchemy.orm as orm
import fastapi.security as security
from starlette.responses import JSONResponse


from services import users as services_users, projects as services_projects, gpt as services_gpt
import schemas
import database


router = fastapi.APIRouter()


@router.post("/api/gpt-query", response_model=schemas.GPTQueryResponse)
async def gpt_query(
    request: schemas.GPTQueryRequest,     
    user: schemas.User = fastapi.Depends(services_users.get_current_user),
    db: orm.Session = fastapi.Depends(database.get_db)
):
    try:
        if not isinstance(request.query, str):
            return JSONResponse(status_code=400, content={"error": "Query must be a string."})

        # Fetch project context if project_id is provided
        project_context = None
        if request.project_id:
            project_context = await services_gpt.get_project_context(db, request.project_id, user.id)

        # Call the GPT service to get the response
        gpt_response = await services_gpt.get_gpt_response(db, request.query, user.id, request.project_id, project_context)
        return schemas.GPTQueryResponse(response=gpt_response)
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})



@router.post("/api/save-chat", response_model=schemas.ChatResponse)
async def save_chat_endpoint(
    chat_request: schemas.ChatCreateRequest,
    db: orm.Session = fastapi.Depends(database.get_db),
    current_user = fastapi.Depends(services_users.get_current_user)
):
    chat = services_gpt.save_chat(
        db=db,
        user_id=current_user.id,
        query=chat_request.query,
        response=chat_request.response,
        project_id=chat_request.project_id,
    )
    return chat



@router.get("/api/get-chats", response_model=schemas.ChatListResponse)
async def get_chats_endpoint(
    db: orm.Session = fastapi.Depends(database.get_db),
    current_user = fastapi.Depends(services_users.get_current_user)
):
    chats = services_gpt.get_chats(db, user_id=current_user.id)
    return {"chats": chats}



