import fastapi
import sqlalchemy.orm as orm
import typing
import passlib.hash as hash
import jwt as jwt


import models
import schemas
import database



async def get_user_by_username(username: str, db: orm.Session):
    return db.query(models.User).filter(models.User.username == username).first()


async def create_user(user: schemas.UserCreate, db: orm.Session):
    user_obj = models.User(
        username=user.username, hashed_password=hash.bcrypt.hash(user.hashed_password)
    )
    db.add(user_obj)
    db.commit()
    db.refresh(user_obj)
    return user_obj


async def authenticate_user(username: str, password: str, db: orm.Session):
    user = await get_user_by_username(db=db, username=username)

    if not user:
        return False

    if not user.verify_password(password):
        return False

    return user


async def create_token(user: models.User):
    user_obj = schemas.User.from_orm(user)

    token = jwt.encode(user_obj.dict(), database.JWT_SECRET)

    return dict(access_token=token, token_type="bearer")


async def get_current_user(
    db: orm.Session = fastapi.Depends(database.get_db),
    token: str = fastapi.Depends(database.oauth2schema),
):
    try:
        payload = jwt.decode(token, database.JWT_SECRET, algorithms=["HS256"])
        user = db.query(models.User).get(payload["id"])
    except:
        raise fastapi.HTTPException(
            status_code=401, detail="Invalid Email or Password"
        )

    return schemas.User.from_orm(user)




