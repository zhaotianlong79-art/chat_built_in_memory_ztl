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



    class Config:
        env_file = ".env"


settings = Settings()

if __name__ == '__main__':
    print(settings)
