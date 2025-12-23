from typing import List

from fastapi import APIRouter, UploadFile, File

from src.schemas.doc2kb_schemas import DocKnowledgeBase
from src.schemas.response import response_success
from src.service.doc2kb_service import PDFToImageService

router = APIRouter()


@router.post("/doc2pdf")
async def doc2knowledge_base(files: List[UploadFile] = File(...)):
    pass


@router.post("/pdf2knowledge_base")
async def pdf2knowledge_base(files: List[UploadFile] = File(...)):
    pdf_service = PDFToImageService()
    res = []
    for file in files:
        image_data = await pdf_service.convert_pdf_to_images(pdf_file=file)
        res.append({"file": file.filename, "image": image_data})

    return response_success(data=res)

