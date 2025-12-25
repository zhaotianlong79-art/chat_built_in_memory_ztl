import asyncio
from functools import lru_cache
from typing import List

from fastapi import APIRouter, UploadFile, File, Form, Depends

from src.schemas.response import response_success, response_error
from src.service.doc2kb_service import PDFToImageService

router = APIRouter()


@router.post("/doc2pdf")
async def doc2knowledge_base(files: List[UploadFile] = File(...)):
    pass


# 创建依赖函数
@lru_cache
def get_pdf_service():
    """获取PDF服务单例"""
    return PDFToImageService()


@router.post("/pdf2knowledge_base")
async def pdf2knowledge_base(
        files: List[UploadFile] = File(..., description="上传文件列表"),
        knowledge_base_id: str = Form(..., description="知识库名字"),
        pdf_service: PDFToImageService = Depends(get_pdf_service)
):
    if not files:
        return response_error(message="请至少上传一个文件")

    # 创建并发的任务列表
    tasks = []
    for file in files:
        task = pdf_service.convert_pdf_to_images(
            pdf_file=file,
            knowledge_base_id=knowledge_base_id
        )
        tasks.append(task)

    # 并发执行所有任务
    image_data_list = await asyncio.gather(*tasks)

    # 组装结果
    res = [
        {"file": file.filename, "image": image_data}
        for file, image_data in zip(files, image_data_list)
    ]

    return response_success(data={"msg": "入库成功" if res else "入库失败"})
