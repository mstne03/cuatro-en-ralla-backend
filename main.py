from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config import settings
from firebase_admin_init import get_firebase_app
from routers import auth, lobby, ws as ws_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    get_firebase_app()
    yield


app = FastAPI(title="Cuatro en Ralla API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/auth")
app.include_router(lobby.router, prefix="/lobby")
app.include_router(ws_router.router)
