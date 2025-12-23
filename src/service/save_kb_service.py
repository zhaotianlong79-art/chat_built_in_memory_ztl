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
