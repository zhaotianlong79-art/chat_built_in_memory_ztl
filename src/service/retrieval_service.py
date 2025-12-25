import traceback
from typing import List, Any, Dict

from loguru import logger

from src.config.config import settings
from src.db_conn.milvus import get_milvus_client
from src.schemas.retrieval_schemas import SearchDocumentImagesParams
from src.service.embed_service import embed_text

milvus = get_milvus_client()


async def get_embedding(text) -> List[float]:
    try:
        custom_input = [
            {"text": text}
        ]
        embedding = await embed_text(custom_input=custom_input)
        return embedding[0].get("embedding")
    except Exception as e:
        logger.error(f"get_embedding: {traceback.format_exc()}")
        raise Exception(f"get embedding error text: {text}")


def get_filter_conditions(search_params: SearchDocumentImagesParams):
    # 构建过滤条件
    _filter = f"knowledge_base_id == '{search_params.knowledge_base_id}'"
    if search_params.file_ids:
        file_ids_str = ", ".join(str(id) for id in search_params.file_ids)
        _filter += f" and file_id in [{file_ids_str}]"
    return _filter


async def _get_formatted_results(
        search_params: SearchDocumentImagesParams,
        results: list[list[dict]]
) -> List[Dict[str, Any]]:
    """ 结果格式化"""
    formatted_results = []
    for hits in results:
        for hit in hits:
            similarity = hit.get('distance')  # IP 相似度越大越相似

            formatted_results.append({
                "id": hit.get("id"),
                "image_url": hit.get("entity").get("image_url"),
                "image_height": hit.get("entity").get("image_height"),
                "image_width": hit.get("entity").get("image_width"),
                "score": similarity,  # score = 相似度
                "file_page": hit.get("entity").get("file_page"),
                "file_id": hit.get("entity").get("file_id"),
                "file_name": hit.get("entity").get("file_name"),
            })

    if search_params.min_similarity is not None:
        formatted_results = [r for r in formatted_results if r["score"] >= search_params.min_similarity]
    return formatted_results


async def retrieval_image(params: SearchDocumentImagesParams) -> list[dict[str, Any]]:
    try:
        _filter = get_filter_conditions(params)

        output_fields = ["image_url", "image_height", "image_width", "file_page", "file_id", "file_name"]

        query_vectors = await get_embedding(params.query)

        results = milvus.search(
            collection_name=settings.MILVUS_DB_COLLECTION_NAME,
            query_vectors=[query_vectors],
            search_params=settings.SEARCH_CONFIG,
            output_fields=output_fields,
            limit=params.limit,
            filter=_filter
        )
        return await _get_formatted_results(params, results)

    except Exception as e:
        logger.error(f"retrieval_image: {traceback.format_exc()}")
        raise Exception(f"retrieval image error params: {params}")
