import fastapi
import requests
import sqlalchemy.orm as orm
import datetime
import json

import models
from services import gpt as services_gpt

BASE_URL = "https://slack.com/api"


def save_slack_token(db: orm.Session, project_id: int, access_token: str) -> models.Project:
    """
    Save or update the Slack access token for a project's integration.
    """
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not project:
        raise fastapi.HTTPException(status_code=404, detail="Project not found.")
    
    if not project.slack_integration:
        raise fastapi.HTTPException(status_code=400, detail="Slack integration not configured for this project.")
    
    project.slack_integration.access_token = access_token
    db.commit()
    db.refresh(project)
    return project


def get_slack_token(db: orm.Session, project_id: int) -> str:
    """
    Retrieve the Slack access token for a project's integration.
    """
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not project or not project.slack_integration:
        raise fastapi.HTTPException(status_code=404, detail="Slack integration not found for this project.")
    
    if not project.slack_integration.access_token:
        raise fastapi.HTTPException(status_code=400, detail="Slack access token not found for this project.")
    
    return project.slack_integration.access_token


def generate_oauth_url(client_id: str, redirect_uri: str, project_id: int) -> str:
    return (
        f"https://slack.com/oauth/v2/authorize"
        f"?client_id={client_id}&scope=channels:read,chat:write,users:read"
        f"&redirect_uri={redirect_uri}"
        f"&state={project_id}"
    )


def handle_slack_callback(code: str, db: orm.Session, project_id: int):
    """
    Handle the OAuth callback and exchange the code for an access token.
    """
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not project:
        raise fastapi.HTTPException(status_code=404, detail="Project not found.")

    slack_integration = db.query(models.SlackIntegration).filter(
        models.SlackIntegration.project_id == project_id
    ).first()
    if not slack_integration:
        raise ValueError("Slack configuration not found for the project.")

    response = requests.post(
        f"{BASE_URL}/oauth.v2.access",
        data={
            "client_id": slack_integration.client_id,
            "client_secret": slack_integration.client_secret,
            "code": code,
            "redirect_uri": slack_integration.redirect_uri,
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    response_data = response.json()

    if not response_data.get("ok"):
        raise ValueError(f"Slack OAuth failed: {response_data.get('error')}")

    save_slack_token(db, project_id, response_data["access_token"])


def associate_slack_with_project(
    db: orm.Session,
    user_id: int,
    project_id: int,
    client_id: str,
    client_secret: str,
    redirect_uri: str,
):
    project = db.query(models.Project).filter(
        models.Project.id == project_id, models.Project.owner_id == user_id
    ).first()
    if not project:
        raise fastapi.HTTPException(status_code=404, detail="Project not found or unauthorized access.")

    slack_integration = db.query(models.SlackIntegration).filter(
        models.SlackIntegration.project_id == project_id
    ).first()

    if not slack_integration:
        slack_integration = models.SlackIntegration(
            project_id=project_id,
            client_id=client_id,
            client_secret=client_secret,
            redirect_uri=redirect_uri,
        )
        db.add(slack_integration)
    else:
        slack_integration.client_id = client_id
        slack_integration.client_secret = client_secret
        slack_integration.redirect_uri = redirect_uri

    db.commit()
    db.refresh(slack_integration)
    return slack_integration





















def get_channels(db: orm.Session, project_id: int):
    """
    Fetch a list of channel names in the Slack workspace.
    """
    access_token = get_slack_token(db, project_id)
    url = f"{BASE_URL}/conversations.list"
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(url, headers=headers)
    data = response.json()
    if not data.get("ok"):
        raise Exception(f"Slack API error: {data.get('error')}")
    return [{"id": channel["id"], "name": channel["name"]} for channel in data.get("channels", [])]


def send_message(db: orm.Session, project_id: int, channel_id: str, message: str):
    """
    Send a message to a Slack channel.
    """
    access_token = get_slack_token(db, project_id)
    payload = {"channel": channel_id, "text": message}
    headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}
    response = requests.post(f"{BASE_URL}/chat.postMessage", json=payload, headers=headers)
    data = response.json()
    if not data.get("ok"):
        raise Exception(f"Slack API error: {data.get('error')}")
    return {"message": "Message sent successfully", "data": data}


def get_messages(db: orm.Session, project_id: int, channel_id: str) -> str:
    """
    Retrieve past messages from a Slack channel as a formatted string.
    """
    access_token = get_slack_token(db, project_id)
    url = f"{BASE_URL}/conversations.history"
    headers = {"Authorization": f"Bearer {access_token}"}
    params = {"channel": channel_id, "limit": 10}
    response = requests.get(url, headers=headers, params=params)
    data = response.json()
    if not data.get("ok"):
        raise Exception(f"Slack API error: {data.get('error')}")

    formatted_messages = []
    for msg in data.get("messages", []):
        user_id = msg.get("user")
        text = msg.get("text")
        timestamp = datetime.datetime.fromtimestamp(float(msg.get("ts"))).strftime("%Y-%m-%d %H:%M:%S")

        # Get user info
        user_name = get_user_info(access_token, user_id)

        formatted_messages.append(
            f"Username: {user_name}, Message: {text}, Date: {timestamp}"
        )
    
    return "\n\n".join(formatted_messages)





def get_user_info(access_token: str, user_id: str):
    """
    Retrieve user information (e.g., real name) from Slack.
    """
    url = f"{BASE_URL}/users.info"
    headers = {"Authorization": f"Bearer {access_token}"}
    params = {"user": user_id}
    response = requests.get(url, headers=headers, params=params)
    data = response.json()
    if not data.get("ok"):
        return user_id
    user_info = data.get("user", {})
    return user_info.get("real_name", user_info.get("name", user_id))


async def handle_slack_message(db: orm.Session, query: str, project_id: int) -> str:
    """
    Handle Slack message requests using GPT and perform Slack operations.
    """
    try:
        # Use GPT to parse the query and determine the action
        system_message = (
            "You are an assistant that processes Slack message requests. "
            "The query might ask to send a message, retrieve messages, fetch channel lists, "
            "or perform other Slack actions. Respond with a JSON object containing "
            "'action' (e.g., 'send', 'get', 'list_channels'), 'channel_name' (if applicable), "
            "'message' (if applicable), and other details."
        )
        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": query},
        ]

        response = services_gpt.client.chat.completions.create(
            model="gpt-3.5-turbo", messages=messages, temperature=0
        )

        parsed_response = response.choices[0].message.content

        # Parse the response into a Python dictionary
        action_details = json.loads(parsed_response)
        action = action_details.get("action")
        channel_name = action_details.get("channel_name")
        message = action_details.get("message")

        # Fetch channels if the action is to list channels
        if action == "list_channels":
            channels = get_channels(db=db, project_id=project_id)
            channel_list = "\n".join([f"- {ch['name']}" for ch in channels])
            return f"Available Slack channels:\n\n{channel_list}"

        # For other actions, map the channel name to its ID
        channels = get_channels(db=db, project_id=project_id)
        channel_id = next((ch["id"] for ch in channels if ch["name"] == channel_name), None)

        if action in ["send", "get"] and not channel_id:
            return f"Channel '{channel_name}' not found in Slack workspace."

        # Handle specific actions
        if action == "send":
            if not message:
                return "No message content provided for sending."
            send_message(db=db, project_id=project_id, channel_id=channel_id, message=message)
            return f"Message '{message}' has been sent to Slack channel '{channel_name}'."

        elif action == "get":
            messages = get_messages(db=db, project_id=project_id, channel_id=channel_id)
            return f"Last 10 messages in Slack channel '{channel_name}':\n\n{messages}"

        else:
            return "Invalid action. Please specify 'send', 'get', or 'list_channels'."

    except Exception as e:
        return f"Error handling Slack message: {str(e)}"



