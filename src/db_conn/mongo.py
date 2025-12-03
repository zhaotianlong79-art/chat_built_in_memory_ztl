
from mongoengine import connect, disconnect

from src.config.config import settings


def init_mongo_db():
    connect(
        db=settings.MONGO_DB,
        host=settings.MONGO_HOST,
        port=settings.MONGO_PORT,
        username=settings.MONGO_USER,
        password=settings.MONGO_PASSWORD,
        authentication_source=settings.MONGO_AUTH_SOURCE,
        alias=settings.MONGO_CONN_NAME,
        minPoolSize=5,
        maxPoolSize=50
    )


def close_mongo_db():
    disconnect(alias=settings.MONGO_DB)