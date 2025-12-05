import uvicorn
from fastapi import FastAPI, applications
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from opentelemetry import trace
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.trace import TracerProvider


from src.config.config import settings
from src.config.openapi_docs import get_swagger_ui_html
from src.db_conn.mongo import init_mongo_db, close_mongo_db
from src.handlers import include_routers
from src.middleware.log import init_stdout_logger
from loguru import logger
from contextlib import asynccontextmanager
from fastapi.responses import ORJSONResponse

# 根据是否 debug 获取 api 文档地址, 非 debug 就加上 nginx 配置的路由地址, 这样可以正确访问到项目的静态资源
swagger_js_url = "/static/swagger-ui-bundle.js" if settings.DEBUG else f"{settings.nginx_url}/static/swagger-ui-bundle.js"
swagger_css_url = "/static/swagger-ui.css" if settings.DEBUG else f"{settings.nginx_url}/static/swagger-ui.css"


def swagger_monkey_patch(*args, **kwargs):
    """
    Wrap the function which is generating the HTML for the /docs endpoint and
    overwrite the default values for the swagger js and css.
    """
    # 判断是否为 debug 从而修改 docs接口中 openapi.json 接口的路由
    url_prefix = "" if settings.DEBUG else settings.nginx_url
    return get_swagger_ui_html(
        *args, **kwargs,
        url_prefix=url_prefix,
        swagger_js_url=swagger_js_url,
        swagger_css_url=swagger_css_url,
    )


applications.get_swagger_ui_html = swagger_monkey_patch

init_stdout_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期"""
    logger.info("Starting up")
    init_mongo_db()
    try:
        yield
    finally:
        close_mongo_db()
        logger.info("Application shutdown")


app = FastAPI(lifespan=lifespan, default_response_class=ORJSONResponse)
app.mount("/static", StaticFiles(directory="static"), name="static")

include_routers(app)

# opentelemetry
trace.set_tracer_provider(TracerProvider())
FastAPIInstrumentor.instrument_app(app)

if settings.DEBUG:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # 或指定前端域名（如 "http://localhost:3000"）
        allow_methods=["*"],  # 或显式指定 ["GET", "POST", "OPTIONS"]
        allow_headers=["*"],
        allow_credentials=True,
    )


@app.get("/health")
async def health_check():
    return {"status": "ok"}


