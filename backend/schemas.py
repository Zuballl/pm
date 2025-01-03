import datetime as _dt

import pydantic as _pydantic
import typing as _typing


class _UserBase(_pydantic.BaseModel):
    username: str


class UserCreate(_UserBase):
    hashed_password: str

    class Config:
        from_attributes = True


class User(_UserBase):
    id: int

    class Config:
        from_attributes = True


class _ProjectBase(_pydantic.BaseModel):
    name: str
    department: str
    client: str
    deadline: str
    description: str


class ProjectCreate(_ProjectBase):
    pass


class Project(_ProjectBase):
    id: int
    owner_id: int
    date_created: _dt.datetime
    date_last_updated: _dt.datetime

    class Config:
        from_attributes = True



class GPTQueryRequest(_pydantic.BaseModel):
    query: str
    project_id: _typing.Optional[int] = None

    class Config:
        from_attributes = True

class GPTQueryResponse(_pydantic.BaseModel):
    response: str

    class Config:
        from_attributes = True




class ChatCreateRequest(_pydantic.BaseModel):
    query: str
    response: str
    project_id: _typing.Optional[int] = None

class ChatResponse(_pydantic.BaseModel):
    id: int
    query: str
    response: str
    project_id: _typing.Optional[int]

    class Config:
        from_attributes = True

class ChatListResponse(_pydantic.BaseModel):
    chats: _typing.List[ChatResponse]