import datetime as _dt

import sqlalchemy as _sql
import sqlalchemy.orm as _orm
import passlib.hash as _hash

import database as _database



class User(_database.Base):
    __tablename__ = "users"
    id = _sql.Column(_sql.Integer, primary_key=True, index=True)
    username = _sql.Column(_sql.String, unique=True, index=True)
    hashed_password = _sql.Column(_sql.String)

    projects = _orm.relationship("Project", back_populates="owner")
    chat_history = _orm.relationship("ChatHistory", back_populates="user")

    def verify_password(self, password: str):
        return _hash.bcrypt.verify(password, self.hashed_password)


class Project(_database.Base):
    __tablename__ = "projects"
    id = _sql.Column(_sql.Integer, primary_key=True, index=True)
    owner_id = _sql.Column(_sql.Integer, _sql.ForeignKey("users.id"))

    name = _sql.Column(_sql.String, index=True)
    department = _sql.Column(_sql.String, index=True)
    client = _sql.Column(_sql.String, index=True)
    deadline = _sql.Column(_sql.String, index=True, default="")
    description = _sql.Column(_sql.String, default="")

    date_created = _sql.Column(_sql.DateTime, default=_dt.datetime.utcnow)
    date_last_updated = _sql.Column(_sql.DateTime, default=_dt.datetime.utcnow)

    owner = _orm.relationship("User", back_populates="projects")



class ChatHistory(_database.Base):
    __tablename__ = "chat_history"

    id = _sql.Column(_sql.Integer, primary_key=True, index=True)
    user_id = _sql.Column(_sql.Integer, _sql.ForeignKey("users.id"))
    project_id = _sql.Column(_sql.Integer, nullable=True)  
    query = _sql.Column(_sql.Text, nullable=False)
    response = _sql.Column(_sql.Text, nullable=False)

    user = _orm.relationship("User", back_populates="chat_history")