import fastapi
import sqlalchemy.orm as orm

import database
import models
import schemas
from services import slack as services_slack, users as services_users

router = fastapi.APIRouter()


@router.post("/api/projects/{project_id}/slack/config")
def associate_slack_with_project(
    project_id: int,
    config: schemas.SlackIntegrationBase,
    db: orm.Session = fastapi.Depends(database.get_db),
    user: models.User = fastapi.Depends(services_users.get_current_user),
):
    """
    Associate a Slack app with a specific project.
    """
    return services_slack.associate_slack_with_project(
        db=db,
        user_id=user.id,
        project_id=project_id,
        client_id=config.client_id,
        client_secret=config.client_secret,
        redirect_uri=config.redirect_uri,
    )


@router.get("/api/projects/{project_id}/slack/connect")
def generate_slack_oauth_url(
    project_id: int,
    db: orm.Session = fastapi.Depends(database.get_db),
    user: models.User = fastapi.Depends(services_users.get_current_user),
):
    """
    Generate a Slack OAuth URL for user authentication for a project.
    """
    project = db.query(models.Project).filter(
        models.Project.id == project_id, models.Project.owner_id == user.id
    ).first()
    if not project:
        raise fastapi.HTTPException(status_code=404, detail="Project not found or unauthorized access.")

    slack_integration = db.query(models.SlackIntegration).filter(
        models.SlackIntegration.project_id == project_id
    ).first()
    if not slack_integration:
        raise fastapi.HTTPException(status_code=400, detail="Slack configuration not found for this project.")

    return {
        "url": services_slack.generate_oauth_url(
            client_id=slack_integration.client_id,
            redirect_uri=slack_integration.redirect_uri,
            project_id=project_id,
        )
    }


@router.get("/api/slack/callback")
def slack_callback(
    code: str,
    state: str,
    db: orm.Session = fastapi.Depends(database.get_db),
):
    """
    Handle the Slack OAuth callback and use the state parameter to get the project ID.
    """
    try:
        project_id = int(state)  # Extract project_id from state
        services_slack.handle_slack_callback(code=code, db=db, project_id=project_id)
        
        # Redirect to your app's specific URL after successful integration
        return fastapi.responses.RedirectResponse(url=f"http://localhost:5173/")
    except ValueError:
        raise fastapi.HTTPException(status_code=400, detail="Invalid project ID in state")


