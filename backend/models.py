import datetime as dt

import sqlalchemy as sql
import sqlalchemy.orm as orm
import passlib.hash as hash

import database



class User(database.Base):
    __tablename__ = "users"
    id = sql.Column(sql.Integer, primary_key=True, index=True)
    username = sql.Column(sql.String, unique=True, index=True)
    hashed_password = sql.Column(sql.String)

    projects = orm.relationship("Project", back_populates="owner")
    chat_history = orm.relationship("ChatHistory", back_populates="user")
    clickup_token = orm.relationship("ClickUpToken", back_populates="user")


    def verify_password(self, password: str):
        return hash.bcrypt.verify(password, self.hashed_password)


class Project(database.Base):
    __tablename__ = "projects"
    id = sql.Column(sql.Integer, primary_key=True, index=True)
    owner_id = sql.Column(sql.Integer, sql.ForeignKey("users.id"))
    clickup_list_id = sql.Column(sql.String, nullable=True) 
    slack_integration = orm.relationship("SlackIntegration", back_populates="project", uselist=False)  # Update this


    name = sql.Column(sql.String, index=True)
    department = sql.Column(sql.String, index=True)
    client = sql.Column(sql.String, index=True)
    deadline = sql.Column(sql.String, index=True, default="")
    description = sql.Column(sql.String, default="")

    date_created = sql.Column(sql.DateTime, default=dt.datetime.utcnow)
    date_last_updated = sql.Column(sql.DateTime, default=dt.datetime.utcnow)

    owner = orm.relationship("User", back_populates="projects")



class ChatHistory(database.Base):
    __tablename__ = "chat_history"

    id = sql.Column(sql.Integer, primary_key=True, index=True)
    user_id = sql.Column(sql.Integer, sql.ForeignKey("users.id"))
    project_id = sql.Column(sql.Integer, nullable=True)  
    query = sql.Column(sql.Text, nullable=False)
    response = sql.Column(sql.Text, nullable=False)

    user = orm.relationship("User", back_populates="chat_history")



class ClickUpToken(database.Base):
    __tablename__ = "clickup_token"
    id = sql.Column(sql.Integer, primary_key=True, index=True)
    user_id = sql.Column(sql.Integer, sql.ForeignKey("users.id"))
    api_token = sql.Column(sql.String, nullable=False)

    user = orm.relationship("User", back_populates="clickup_token")



class SlackIntegration(database.Base):
    __tablename__ = "slack_integration"
    id = sql.Column(sql.Integer, primary_key=True, index=True)
    client_id = sql.Column(sql.String, nullable=False)
    client_secret = sql.Column(sql.String, nullable=False)
    redirect_uri = sql.Column(sql.String, nullable=False)
    access_token = sql.Column(sql.String, nullable=True)

    project_id = sql.Column(sql.Integer, sql.ForeignKey("projects.id"), nullable=False)
    project = orm.relationship("Project", back_populates="slack_integration")