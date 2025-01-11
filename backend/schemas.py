import datetime as dt
import pydantic
import typing


class UserBase(pydantic.BaseModel):
    username: str


class UserCreate(UserBase):
    hashed_password: str

    class Config:
        from_attributes = True


class User(UserBase):
    id: int

    class Config:
        from_attributes = True





class GPTQueryRequest(pydantic.BaseModel):
    query: str
    project_id: typing.Optional[int] = None

    class Config:
        from_attributes = True

class GPTQueryResponse(pydantic.BaseModel):
    response: str

    class Config:
        from_attributes = True




class ChatCreateRequest(pydantic.BaseModel):
    query: str
    response: str
    project_id: typing.Optional[int] = None

class ChatResponse(pydantic.BaseModel):
    id: int
    query: str
    response: str
    project_id: typing.Optional[int]

    class Config:
        from_attributes = True

class ChatListResponse(pydantic.BaseModel):
    chats: typing.List[ChatResponse]









class ClickUpConnect(pydantic.BaseModel):
    api_token: str
    list_id: str

class ClickUpTokenCreate(pydantic.BaseModel):
    api_token: str


class ClickUpResponse(pydantic.BaseModel):
    status: str
    message: str


class ClickUpIntegrationBase(pydantic.BaseModel):
    api_token: typing.Optional[str] = None
    list_id: typing.Optional[str] = None

    class Config:
        from_attributes = True










class SlackIntegrationBase(pydantic.BaseModel):
    client_id: str
    client_secret: str
    redirect_uri: str


class SlackIntegrationCreate(SlackIntegrationBase):
    pass


class SlackIntegrationResponse(SlackIntegrationBase):
    id: int
    access_token: typing.Optional[str] = None

    class Config:
        from_attributes = True








class GoogleDriveBase(pydantic.BaseModel):
    client_id: str
    client_secret: str
    token: str

class GoogleDriveCreate(GoogleDriveBase):
    pass

class GoogleDriveResponse(GoogleDriveBase):
    id: int
    project_id: int

    class Config:
        from_attributes = True




    






class ProjectBase(pydantic.BaseModel):
    name: str
    department: str
    client: str
    deadline: str
    description: str
    clickup_integration: typing.Optional[ClickUpIntegrationBase] = None 
    slack_integration: typing.Optional[SlackIntegrationBase] = None

    class Config:
        from_attributes = True


class ProjectCreate(ProjectBase):
    pass


class Project(ProjectBase):
    id: int
    owner_id: int
    date_created: dt.datetime
    date_last_updated: dt.datetime

    class Config:
        from_attributes = True
