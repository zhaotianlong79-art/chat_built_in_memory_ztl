# 保存向量数据在milvus
import os
import traceback
from typing import Any, List

from loguru import logger

from src.config.config import settings
from src.db_conn.milvus import milvus_client as Milvus
from src.schemas.milvus_schemas import EmbedData

Milvus.ensure_collection(settings.MILVUS_DB_NAME)


async def save_kb_milvus(images_data: List[Any]):
    if images_data:
        try:
            batch_size = 80
            for i in range(0, len(images_data), batch_size):
                batch = images_data[i:i + batch_size]
                Milvus.insert(data=batch)
        except Exception as e:
            logger.error(f"save_kb_milvus error: {e}")
            raise traceback.format_exception()

    logger.info("save_kb_milvus success")


def truncate_filename(filename, max_length=25):
    """milvus使用字节长度，一个中文是三字节25*3=75"""
    filename = filename[8:]  # 去掉前缀的随机生产的uid
    if len(filename) > max_length:
        # 保留扩展名，截断主体部分
        name, ext = os.path.splitext(filename)
        truncated_name = name[:max_length - len(ext) - 1]  # -1 用于省略号
        return f"{truncated_name}...{ext}"
    return filename


def get_default_dict(image_data: EmbedData):
    return {
        "embedding": image_data.embedding,
        "image_url": image_data.image_url,
        "image_width": image_data.image_width,
        "image_height": image_data.image_height,
        "image_size": image_data.image_size,
        "file_id": image_data.file_id,
        "file_name": truncate_filename(image_data.file_name),
        "file_page": image_data.file_page,
        "file_url": image_data.file_url,
        "knowledge_base_id": image_data.knowledge_base_id,
    }
