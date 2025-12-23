from fastapi import APIRouter, UploadFile, File

from src.repositories.knowledge_repository import create_knowledge_base, update_knowledge_base
from src.schemas.knowledge_base_schemas import (
    CreateKnowledgeBaseParams,
    UpdateKnowledgeBaseParams
)
from src.schemas.response import response_success, response_error

router = APIRouter()


@router.post("/create")
async def create_kb_data(params: CreateKnowledgeBaseParams):
    try:
        kb = create_knowledge_base(params.knowledge_description, params.knowledge_name)
        return response_success(data=kb)
    except Exception as e:
        return response_error(str(e))


@router.post("/update")
async def update_kb_data(params: UpdateKnowledgeBaseParams):
    try:
        kb = update_knowledge_base(params.knowledge_base_id, params.knowledge_description, params.knowledge_name)
        return response_success(data=kb)
    except Exception as e:
        return response_error(str(e))
