import fastapi
import sqlalchemy.orm as orm
from openai import OpenAI
import typing
import os
import re

import models
from services import clickup as services_clickup, slack as services_slack

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))



async def get_project_context(db: orm.Session, project_id: int, user_id: int):
    """
    Fetch project details for a given project_id from the database.
    """
    project = db.query(models.Project).filter(
        models.Project.id == project_id, 
        models.Project.owner_id == user_id  
    ).first()

    if not project:
        raise fastapi.HTTPException(status_code=404, detail="Project is not found or you are not authorised to access it.")
    return {
        "Project Name": project.name,
        "Department": project.department,
        "Client": project.client,
        "Deadline": project.deadline,
        "Description": project.description,

    }





async def get_gpt_response(
    db: orm.Session, query: str, user_id: int, project_id: typing.Optional[int] = None, project_context: dict = None
) -> str:
    try:
        # Check if the query is ClickUp-related
        if "clickup" in query.lower():
            if not project_id:
                return "Please specify a project to associate this ClickUp operation."
            return await services_clickup.handle_clickup_task(db, query, project_id)

        if "slack" in query.lower():
            if not project_id:
                return "Please specify a project to associate this Slack operation."
            return await services_slack.handle_slack_message(db, query, project_id)


        # Handle standard GPT response
        system_message = f"Context: {project_context}" if project_context else "General Query"
        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": query},
        ]
        response = client.chat.completions.create(
            model="gpt-3.5-turbo", messages=messages, temperature=0.7
        )
        gpt_response = response.choices[0].message.content
        save_chat(db, user_id=user_id, query=query, response=gpt_response, project_id=project_id)
        return gpt_response

    except Exception as e:
        raise Exception(f"Error querying GPT: {str(e)}")



def save_chat(
    db: orm.Session, user_id: int, query: str, response: str, project_id: typing.Optional[int] = None
):
    new_chat = models.ChatHistory(
        user_id=user_id, query=query, response=response, project_id=project_id
    )
    db.add(new_chat)
    db.commit()
    db.refresh(new_chat)
    return new_chat

def get_chats(db: orm.Session, user_id: int):
    return db.query(models.ChatHistory).filter(models.ChatHistory.user_id == user_id).all()




