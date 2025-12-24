import traceback

from loguru import logger

from src.models.mongo import Files


async def create_file_data(
        file_name: str,
        file_size: str,
        file_url: str,
        file_type: str,
        knowledge_base_id: str,
) -> Files:
    try:
        session = Files.objects.create(
            file_name=file_name,
            file_size=file_size,
            file_url=file_url,
            file_type=file_type,
            knowledge_base_id=knowledge_base_id
        )
        session.save()
        return session
    except Exception as e:
        logger.error(f"Error creating file: {traceback.format_exception()}")
        raise Exception("Error creating file")


async def delete_file_data(file_id: str):
    try:
        session = Files.objects.get(id=file_id)
        # 删除知识库
        session.delete()
        return True
    except Exception as e:
        logger.error(f"del file_data {file_id} does not exist")
        raise Exception("Error deleting file_data")


async def select_file_data(file_id: str) -> Files:
    try:
        session = Files.objects.get(id=file_id)
        return session
    except Exception as e:
        logger.error(f"Error selecting file: {traceback.format_exception()}")
        raise Exception("Error selecting file")


async def update_file_data(
        file_id: str,
        file_name: str,
        file_size: str,
        file_url: str,
        file_type: str,
        knowledge_base_id: str
) -> Files:
    try:
        session = Files.objects.get(id=file_id)
        session.file_name = file_name
        session.file_size = file_size
        session.file_url = file_url
        session.file_type = file_type
        session.knowledge_base_id = knowledge_base_id
        session.save()
        return session
    except Exception as e:
        logger.error(f"Error updating file: {traceback.format_exception()}")
        raise Exception("Error updating file")
