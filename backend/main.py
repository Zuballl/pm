import fastapi as fastapi
from fastapi.middleware.cors import CORSMiddleware

from routers import users, projects, gpt, clickup



app = fastapi.FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(users.router)
app.include_router(projects.router)
app.include_router(gpt.router)
app.include_router(clickup.router)







