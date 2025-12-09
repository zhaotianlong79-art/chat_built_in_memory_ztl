from typing import List

from fastapi import APIRouter, UploadFile, File

from src.schemas.doc2kb_schemas import DocKnowledgeBase

router = APIRouter()


@router.post("/doc2knowledge_base")
async def doc2knowledge_base(params: DocKnowledgeBase):
    pass


@router.post("/doc2knowledge_base")
async def doc2knowledge_base(files: List[UploadFile] = File(...)):
    pass
