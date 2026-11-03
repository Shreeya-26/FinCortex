from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from . import config, database, scoring
from .routes import router


@asynccontextmanager
async def lifespan(_: FastAPI):
    database.init_db()
    if not scoring.load_model():
        print("WARNING: ml/model.pkl not found. Train the model first (see README).")
    yield


app = FastAPI(title="FinCortex API", version="1.0.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.allowed_origins(),
    allow_methods=["GET", "POST", "DELETE"],
    allow_headers=["Content-Type"],
)
app.include_router(router)
