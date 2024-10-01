from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from redis import asyncio as aioredis

from auth.base_config import auth_backend, fastapi_users
from auth.schemas import UserRead, UserCreate
from config import REDIS_HOST, REDIS_PORT
from operations.router import router as router_operation
from tasks.router import router as router_tasks
from pages.router import router as router_pages

from chat.router import router as router_chat

app = FastAPI(
    title="Neuron messenger"
)

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/auth",
    tags=["Auth"],
)

app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["Auth"],
)

app.include_router(router_operation)
app.include_router(router_tasks)
app.include_router(router_pages) # подключаем роутер с Jinja
app.include_router(router_chat)

# адреса фронтов котрые имеют доступ к бекенду
origins = [
    "http://localhost:8080",
]

# добавление корс миделвара
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS", "DELETE", "PATCH", "PUT"],
    allow_headers=["Content-Type", "Set-Cookie", "Access-Control-Allow-Headers", "Access-Control-Allow-Origin",
                   "Authorization"],
)

# alembic init migrations
# alembic revision --autogenerate -m "Database create"
# alembic upgrade cb52a184c0f9 или head

# celery -A tasks.tasks:celery worker --loglevel=INFO # выриант celery

# celery -A tasks.tasks:celery flower   # web interface  localhost : 5555

@app.on_event("startup")
async def startup_event():
    redis = aioredis.from_url(f"redis://{REDIS_HOST}:{REDIS_PORT}", encoding="utf8", decode_responses=True)
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")

# docker compose build
# docker compose up