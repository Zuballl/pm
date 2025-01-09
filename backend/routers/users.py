import fastapi
import sqlalchemy.orm as orm
import fastapi.security as security

from services import users as services_users
import schemas
import database

router = fastapi.APIRouter()


@router.post("/api/users")
async def create_user(
    user: schemas.UserCreate, db: orm.Session = fastapi.Depends(database.get_db)
):
    db_user = await services_users.get_user_by_username(user.username, db)
    if db_user:
        raise fastapi.HTTPException(status_code=400, detail="Username already exists")

    new_user = await services_users.create_user(user, db)

    # Generate token for the new user
    token = await services_users.create_token(new_user)

    return token



@router.post("/api/token")
async def generate_token(
    form_data: security.OAuth2PasswordRequestForm = fastapi.Depends(),
    db: orm.Session = fastapi.Depends(database.get_db),
):
    user = await services_users.authenticate_user(form_data.username, form_data.password, db)

    if not user:
        raise fastapi.HTTPException(status_code=401, detail="Invalid Credentials")

    return await services_users.create_token(user)


@router.get("/api/users/me", response_model=schemas.User)
async def get_user(user: schemas.User = fastapi.Depends(services_users.get_current_user)):
    return user
