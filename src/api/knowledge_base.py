from fastapi import APIRouter

from src.repositories.knowledge_repository import (
    create_knowledge_base,
    update_knowledge_base,
    delete_knowledge_base,
    select_knowledge_bases,
    select_knowledge_file
)
from src.schemas.knowledge_base_schemas import (
    CreateKnowledgeBaseParams,
    UpdateKnowledgeBaseParams,
    SelectKnowledgeBaseParams,
    SelectKnowledgeBaseFilesParams
)
from src.schemas.response import response_success, response_error

router = APIRouter()


@router.post("/select")
async def select_kb_data(params: SelectKnowledgeBaseParams):
    try:
        kb = await select_knowledge_bases(
            page=params.page,
            page_size=params.page_size,
            knowledge_name=params.knowledge_name,
            order_by=params.order_by
        )
        return response_success(data=kb)
    except Exception as e:
        return response_error(str(e))


@router.post("/select_files")
async def select_kb_data(params: SelectKnowledgeBaseFilesParams):
    try:
        kb = await select_knowledge_file(
            knowledge_base_id=params.knowledge_base_id,
            page=params.page,
            page_size=params.page_size,
            file_name=params.file_name,
            file_type=params.file_type,
            order_by=params.order_by
        )
        return response_success(data=kb)
    except Exception as e:
        return response_error(str(e))


@router.post("/create")
async def create_kb_data(params: CreateKnowledgeBaseParams):
    try:
        kb = await create_knowledge_base(
            knowledge_description=params.knowledge_description,
            knowledge_name=params.knowledge_base_name
        )
        return response_success(data=kb.to_dict())
    except Exception as e:
        return response_error(str(e))


@router.post("/update")
async def update_kb_data(params: UpdateKnowledgeBaseParams):
    try:
        kb = await update_knowledge_base(
            params.knowledge_base_id,
            params.knowledge_description,
            params.knowledge_base_name
        )
        return response_success(data=kb.to_dict())
    except Exception as e:
        return response_error(str(e))


@router.delete("/delete")
async def delete_kb_data(params: UpdateKnowledgeBaseParams):
    try:
        kb = await delete_knowledge_base(params.knowledge_base_id)
        return response_success(data=kb)
    except Exception as e:
        return response_error(str(e))
