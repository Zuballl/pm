import fastapi as fastapi
from fastapi.middleware.cors import CORSMiddleware

from routers import users, projects, gpt, clickup, slack



app = fastapi.FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(users.router, tags=["Users"])
app.include_router(projects.router, tags=["Projects"])
app.include_router(gpt.router, tags=["GPT"])
app.include_router(clickup.router, tags=["Clickup"])
app.include_router(slack.router, tags=["Slack"])







