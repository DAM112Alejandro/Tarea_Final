from fastapi import FastAPI
from auth.auth import router as auth_router
from routers import users , events , registrations

app = FastAPI()

app.include_router(auth_router)
app.include_router(users.router)
app.include_router(events.router)
app.include_router(registrations.router)