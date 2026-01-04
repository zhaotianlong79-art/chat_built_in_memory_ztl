from typing import List

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # 日志配置
    log_rotation: str = "100 MB"
    log_retention: str = "7 days"
    log_compression: str = "gz"
    log_time_format: str = "YYYY-MM-DD HH:mm:ss.SSSSSS ZZ zz"
    no_print_request_body_list: List[str] = ["/file/upload"]
    access_log_format: str = (
        "{process_time}ms - {status_code} - {client_ip} - {user}/{uid} - {ua} " "- {method} {path} - {request_body}"
    )
    access_log_file: str = ""
    access_log_level: str = "INFO"
    access_log_enable: bool = False
    access_log_response: bool = False
    api_log_file: str = ""
    api_log_level: str = "INFO"
    celery_log_file: str = ""
    celery_log_level: str = "INFO"
    normal_log_file: str = ""
    normal_log_level: str = "INFO"
    stdout_log_file: str = ""
    stdout_log_level: str = "INFO"

    DEBUG: bool = True

    SEARCH_CONFIG: dict = {
        "metric_type": "IP",  # 使用内积相似度
        "params": {"ef": 128},
    }

    MONGO_DB: str = "zkm_test"
    MONGO_HOST: str = "XXX"
    MONGO_PORT: int = 27017
    MONGO_USER: str = "admin"
    MONGO_PASSWORD: str = "XXX"
    MONGO_AUTH_SOURCE: str = "admin"
    MONGO_CONN_NAME: str = "default"

    MILVUS_DB_HOST: str = "XXX"
    MILVUS_DB_PORT: int = 29530
    MILVUS_DB_NAME: str = "default"
    MILVUS_DB_USER: str = ""
    MILVUS_DB_PASS: str = ""
    MILVUS_DB_TIMEOUT: int = 30
    MILVUS_DB_COLLECTION_NAME: str = "zkm_test"


    EMBED_SERVER_URL: str = "https://api.jina.ai/v1/embeddings"
    EMBED_SERVER_TOKEN: str = "XXX"

    IMAGE_DPI: int = 160
    IMAGE_UPLOAD_SERVE: str = "XXXX"
    IMAGE_MAX_WORKERS: int = 4

    MODEL_NAME: str = "qwen",
    MODEL_API_KEY: str = "XXX",
    MODEL_BASE_URL: str = "http://XXXX/v1"

    class Config:
        env_file = ".env"


settings = Settings()

if __name__ == '__main__':
    print(settings)
