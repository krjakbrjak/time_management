from fastapi import FastAPI

from time_manager.routers import auth, users

app = FastAPI(
    title="Time manager",
    description="Time tracking tool",
    version="0.0.1",
)

app.include_router(users.router)
app.include_router(auth.router)
