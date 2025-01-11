import fastapi
import sqlalchemy.orm as orm
import requests
import json
import datetime as dt

import models
import schemas
from services import gpt as services_gpt




def connect_project_to_clickup(db: orm.Session, project_id: int, user: models.User, api_token: str, list_id: str):
    """
    Save or update the ClickUp integration (token and list ID) for a specific project.
    Filters projects by the logged-in user.
    """
    # Query the project and ensure it belongs to the current user
    project = (
        db.query(models.Project)
        .filter(models.Project.id == project_id, models.Project.owner_id == user.id)
        .first()
    )

    if not project:
        raise fastapi.HTTPException(status_code=404, detail="Project not found or unauthorized access")

    # Check if integration already exists
    if project.clickup_integration:
        # Update the existing integration
        project.clickup_integration.api_token = api_token
        project.clickup_integration.list_id = list_id
    else:
        # Create a new integration
        integration = models.ClickUpIntegration(
            project_id=project_id,
            api_token=api_token,
            list_id=list_id,
        )
        db.add(integration)

    db.commit()
    db.refresh(project)
    return project





# Get ClickUp Integration for a Project
def get_clickup_integration(db: orm.Session, project_id: int):
    """
    Fetch the ClickUp integration for a specific project.
    """
    return (
        db.query(models.ClickUpIntegration)
        .filter(models.ClickUpIntegration.project_id == project_id)
        .first()
    )




def get_clickup_token(db: orm.Session, project_id: int):
    """
    Retrieve the ClickUp API token for a specific project.

    Args:
        db (orm.Session): Database session.
        project_id (int): The ID of the project.

    Returns:
        models.ClickUpIntegration: The ClickUp integration for the project, or None if not found.
    """
    integration = (
        db.query(models.ClickUpIntegration)
        .filter(models.ClickUpIntegration.project_id == project_id)
        .first()
    )
    if not integration:
        raise fastapi.HTTPException(
            status_code=404, detail=f"No ClickUp integration found for project {project_id}"
        )
    return integration















def add_task_to_clickup(api_token: str, list_id: str, task_name: str, description: str = "", due_date: str = None):
    """
    Add a task to ClickUp.

    Args:
        api_token (str): ClickUp API token.
        list_id (str): ID of the ClickUp list.
        task_name (str): Name of the task to create.
        description (str, optional): Description of the task.
        due_date (str, optional): Due date of the task in ISO format (e.g., '2025-01-01').

    Returns:
        dict: JSON response from the ClickUp API.
    """
    headers = {
        "Authorization": api_token,
        "Content-Type": "application/json",
    }

    if due_date:
        try:
            # Convert string to datetime object and then to milliseconds
            due_date_obj = dt.datetime.strptime(due_date, "%Y-%m-%d")
            due_date_ms = int(due_date_obj.timestamp() * 1000)
        except ValueError:
            raise ValueError("Invalid due_date format. Expected format: 'YYYY-MM-DD'")
    else:
        due_date_ms = None

    data = {
        "name": task_name,
        "description": description,
        "due_date": due_date_ms,
    }

    # Remove `due_date` if it's None
    data = {key: value for key, value in data.items() if value is not None}

    response = requests.post(f"https://api.clickup.com/api/v2/list/{list_id}/task", json=data, headers=headers)
    response.raise_for_status()
    return response.json()



def update_task_in_clickup(api_token: str, task_id: str, updates: dict):
    """
    Update an existing task in ClickUp.

    Args:
        api_token (str): ClickUp API token.
        task_id (str): ID of the ClickUp task to update.
        updates (dict): Fields to update (e.g., {'name': 'New Task Name', 'description': 'Updated description'}).

    Returns:
        dict: JSON response from the ClickUp API.
    """
    headers = {"Authorization": api_token, "Content-Type": "application/json"}
    response = requests.put(f"https://api.clickup.com/api/v2/task/{task_id}", json=updates, headers=headers)
    response.raise_for_status()
    return response.json()


def delete_task_from_clickup(api_token: str, task_id: str):
    """
    Delete a task from ClickUp.

    Args:
        api_token (str): ClickUp API token.
        task_id (str): ID of the ClickUp task to delete.

    Returns:
        None
    """
    
    headers = {"Authorization": api_token}
    response = requests.delete(f"https://api.clickup.com/api/v2/task/{task_id}", headers=headers)
    response.raise_for_status()



def get_task_by_name(api_token: str, list_id: str, task_name: str) -> dict:
    tasks = get_all_tasks_from_clickup(api_token, list_id)
    for task in tasks:
        if task.get("name", "").lower() == task_name.lower():
            if task.get("creator", {}).get("id") != api_token:
                raise PermissionError(f"Task '{task_name}' exists but is owned by another user.")
            return task
    raise ValueError(f"Task with name '{task_name}' not found.")



def get_all_tasks_from_clickup(api_token: str, list_id: str) -> list:
    """
    Fetch all tasks from a specific ClickUp list.

    Args:
        api_token (str): ClickUp API token.
        list_id (str): ID of the ClickUp list.

    Returns:
        list: List of tasks from the ClickUp API.
    """
    headers = {"Authorization": api_token}
    response = requests.get(f"https://api.clickup.com/api/v2/list/{list_id}/task", headers=headers)
    response.raise_for_status()
    return response.json().get("tasks", [])



def format_task_list_response(tasks: list, project_name: str) -> str:
    """
    Formats the task list for a user-friendly response.
    """
    if not tasks:
        return f"No tasks found in the ClickUp list associated with project '{project_name}'."

    formatted_tasks = "\n\n".join(
        [
            f"Task Name: {task.get('name', 'No Name')},\n"
            f"Task Description: {task.get('description', 'No Description')},\n"
            f"Task Due Date: {format_due_date(task.get('due_date'))}."
            for task in tasks
        ]
    )
    return formatted_tasks





def format_due_date(due_date_ms):
    if due_date_ms:
        try:
            due_date = dt.datetime.fromtimestamp(int(due_date_ms) / 1000).strftime("%Y-%m-%d")
            return due_date
        except (ValueError, TypeError):
            return "Invalid Due Date"
    return "No Due Date"











async def handle_clickup_task(db: orm.Session, query: str, project_id: int) -> str:
    try:
        # Use GPT to parse the query and determine the action
        system_message = (
            "You are an assistant that processes ClickUp task requests. "
            "The query might ask to create, update, delete, or retrieve tasks. "
            "Respond with a JSON object containing 'action' (e.g., 'add', 'update', 'delete', 'get', 'get_all'), "
            "'task_name' (if applicable), 'task_id' (if applicable), 'description' (if applicable), 'due_date' (if applicable), and other details."
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
        try:
            task_details = json.loads(parsed_response)
            action = task_details.get("action")
            task_name = task_details.get("task_name")
            task_id = task_details.get("task_id")
            description = task_details.get("description", "")
            due_date = task_details.get("due_date", None)
        except json.JSONDecodeError:
            return "Failed to parse task details. Please provide a clearer query."

        # Fetch ClickUp token and list details for the project
        clickup_integration = get_clickup_token(db, project_id)
        api_token = clickup_integration.api_token
        list_id = clickup_integration.list_id

        # Handle actions
        if action == "add":
            add_task_to_clickup(
                api_token=api_token,
                list_id=list_id,
                task_name=task_name,
                description=description,
                due_date=due_date,
            )
            return f"Task '{task_name}' with description '{description or 'None'}' and deadline '{due_date or 'None'}' has been added to the ClickUp list."

        elif action in ["update", "delete"]:
            # Fetch task ID by name if not provided
            if not task_id:
                task = get_task_by_name(
                    api_token=api_token,
                    list_id=list_id,
                    task_name=task_name,
                )
                task_id = task["id"]

            if action == "update":
                updates = {
                    "name": task_name,
                    "description": description,
                    "due_date": (
                        int(dt.datetime.strptime(due_date, "%Y-%m-%d").timestamp() * 1000)
                        if due_date
                        else None
                    ),
                }
                updates = {k: v for k, v in updates.items() if v is not None}  # Remove None values
                update_task_in_clickup(api_token=api_token, task_id=task_id, updates=updates)
                return f"Task '{task_name}' has been updated successfully."

            elif action == "delete":
                delete_task_from_clickup(api_token=api_token, task_id=task_id)
                return f"Task '{task_name}' has been deleted successfully."

        elif action == "get":
            # Fetch task by name if task_id is not provided
            if not task_id:
                task = get_task_by_name(
                    api_token=api_token,
                    list_id=list_id,
                    task_name=task_name,
                )
                task_id = task["id"]
            task = get_task_from_clickup(api_token=api_token, task_id=task_id)
            return f"Task Details:\n{json.dumps(task, indent=2)}"

        elif action == "get_all":
            tasks = get_all_tasks_from_clickup(api_token=api_token, list_id=list_id)
            formatted_tasks = format_task_list_response(tasks, f"Project {project_id}")
            return f"All Tasks in Project {project_id}:\n\n{formatted_tasks}"
        else:
            return "Invalid action. Please specify 'add', 'update', 'delete', 'get', or 'get_all'."

    except Exception as e:
        return f"Error handling ClickUp task: {str(e)}"