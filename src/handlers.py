from fastapi import FastAPI

from src.api.api import api_router


def include_routers(app: FastAPI) -> None:
    app.include_router(api_router)
