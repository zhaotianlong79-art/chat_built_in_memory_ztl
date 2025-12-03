import os
import sys

from loguru import logger
from opentelemetry.trace import get_current_span, format_trace_id

from src.config.config import settings

LOG_FORMAT = "<green>{{time:{}}}</green> | <level>{{level:.4}}</level> | pid={{extra[pid]}} | trace_id={{extra[otelTraceID]}} | <cyan>{{file}}:{{line}}</cyan> | {{message}}"


def get_current_trace_id() -> str:
    """获取当前 trace_id。"""
    span = get_current_span()
    ctx = span.get_span_context()
    return format_trace_id(ctx.trace_id)


def init_logger(log_level: str, log_file: str, filter_func):
    # logger.remove 初始化logger, 把默认的handler都去掉, 只用自己定义的handler
    logger.remove()
    logger.configure(patcher=add_trace_context)
    if log_file:
        sink = log_file
        logger.add(
            sink,
            level=log_level,
            format=LOG_FORMAT.format(settings.log_time_format),
            filter=filter_func,
            rotation=settings.log_rotation,
            retention=settings.log_retention,
            compression=settings.log_compression,
        )
    else:
        sink = sys.stdout
        logger.add(
            sink,
            level=log_level,
            format=LOG_FORMAT.format(settings.log_time_format),
            filter=filter_func,
        )


def init_stdout_logger():
    """
    打印所有日志：logger.info()
    :return:
    """
    pid = os.getpid()
    log_file = settings.stdout_log_file.replace("stdout.log", f"stdout_{pid}.log")
    init_logger(
        settings.stdout_log_level,
        log_file,
        lambda record: True,
    )


def init_celery_logger():
    """
    打印所有日志：logger.info()
    :return:
    """
    pid = os.getpid()
    log_file = settings.celery_log_file.replace("celery_stdout.log", f"celery_stdout_{pid}.log")
    init_logger(
        settings.celery_log_level,
        log_file,
        lambda record: True,
    )


def add_trace_context(record):
    record["extra"]["otelTraceID"] = get_current_trace_id()
    record["extra"]["pid"] = os.getpid()
