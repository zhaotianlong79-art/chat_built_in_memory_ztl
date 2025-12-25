from fastapi import APIRouter

from src.schemas.response import response_success, response_error
from src.schemas.retrieval_schemas import SearchDocumentImagesParams
from src.service.retrieval_service import retrieval_image

router = APIRouter()


@router.post("/doc")
async def search_document_images(params: SearchDocumentImagesParams):
    try:
        data = await retrieval_image(params)
        return response_success(data=data)
    except Exception as e:
        return response_error(str(e))
