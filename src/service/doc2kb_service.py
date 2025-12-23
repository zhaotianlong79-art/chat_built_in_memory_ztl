import asyncio
import io
import os
import tempfile
import time
import traceback
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Any

import fitz  # PyMuPDF
from PIL import Image
from fastapi import UploadFile, HTTPException
from loguru import logger

from src.config.config import settings
from src.schemas.milvus_schemas import EmbedData
from src.service.embed_service import embed_text
from src.utils.images_upload import zhipu_image_upload


def get_embedding(image_url):
    try:
        custom_input = [
            {"image": image_url}
        ]
        embedding = asyncio.run(embed_text(custom_input=custom_input))
        return embedding[0].get("embedding")
    except Exception as e:
        logger.error(f"get_embedding: {traceback.format_exc()}")
        raise Exception(f"get embedding error image_url: {image_url}")


class PDFToImageService:
    def __init__(self):
        self.executor = ThreadPoolExecutor(max_workers=settings.IMAGE_MAX_WORKERS)

    async def convert_pdf_to_images(
            self,
            pdf_file: UploadFile,
            pages: List[int] = None
    ) -> List[Dict[str, Any]]:
        """
        将PDF文件转换为图片列表

        Args:
            pdf_file: 上传的PDF文件
            dpi: 转换DPI（默认为全局DPI）
            pages: 指定转换的页码列表（从1开始），None表示转换所有页

        Returns:
            图片数据列表，每个元素包含图片信息
        """

        # 验证文件类型
        if not pdf_file.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="文件必须是PDF格式")

        try:
            # 创建临时文件保存PDF
            temp_pdf_path = self._save_temp_pdf(pdf_file)

            # 并发处理PDF转换
            images_data = await self._process_pdf_concurrent(temp_pdf_path, pages, pdf_file.filename)

            # 清理临时PDF文件
            self._cleanup_temp_file(temp_pdf_path)

            return images_data

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"PDF转换失败: {str(e)}")

    def _save_temp_pdf(self, pdf_file: UploadFile) -> str:
        """保存PDF到临时文件"""
        temp_id = str(uuid.uuid4())
        temp_pdf_path = os.path.join(tempfile.gettempdir(), f"{temp_id}.pdf")

        # 读取并保存PDF文件
        content = pdf_file.file.read()
        with open(temp_pdf_path, "wb") as f:
            f.write(content)

        return temp_pdf_path

    async def _process_pdf_concurrent(
            self,
            pdf_path: str,
            pages: List[int],
            pdf_filename: str
    ) -> List[Dict[str, Any]]:
        """并发处理PDF转换"""
        start_time = time.time()
        logger.info(f"开始转化为知识库、文件：{pdf_filename}")
        # 打开PDF文件获取总页数
        doc = fitz.open(pdf_path)
        total_pages = doc.page_count

        # 确定要转换的页码
        if pages is None:
            pages_to_convert = list(range(1, total_pages + 1))
        else:
            # 验证页码有效性
            pages_to_convert = []
            for page_num in pages:
                if 1 <= page_num <= total_pages:
                    pages_to_convert.append(page_num)
                else:
                    raise HTTPException(
                        status_code=400,
                        detail=f"页码 {page_num} 超出范围 (1-{total_pages})"
                    )

        doc.close()

        # 提交并发任务
        futures = []
        for page_num in pages_to_convert:
            future = self.executor.submit(
                self._convert_single_page,
                pdf_path,
                page_num,
                pdf_filename
            )
            futures.append(future)

        # 收集结果
        images_data = []
        for future in as_completed(futures):
            try:
                result = future.result()
                images_data.append(result)
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"页面转换失败: {str(e)}")

        # 按页码排序
        # images_data.sort(key=lambda x: x["page_number"])

        end_time = time.time()
        logger.info(f"知识库转完毕、文件：{pdf_filename}、处理时间：{str(end_time - start_time)}秒")
        return images_data

    def _convert_single_page(
            self,
            pdf_path: str,
            page_num: int,
            pdf_filename: str,
            pdf_id: str = "pdf_id",
            pdf_url: str = "pdf_url",
            kb_id: str = "kb_id",
            dpi: int = settings.IMAGE_DPI,
    ) -> EmbedData:
        """转换单个PDF页面为图片"""
        try:
            # 打开PDF文档
            doc = fitz.open(pdf_path)
            page = doc.load_page(page_num - 1)  # fitz页码从0开始

            # 计算缩放比例
            zoom = dpi / 72  # 72是PDF的标准DPI
            mat = fitz.Matrix(zoom, zoom)

            # 渲染页面为像素图
            pix = page.get_pixmap(matrix=mat, alpha=False)

            # 转换为PIL Image获取更多信息
            img_data = pix.tobytes("ppm")
            pil_image = Image.open(io.BytesIO(img_data))

            # 获取图片信息
            width, height = pil_image.size

            # 转换为JPEG格式并压缩
            img_byte_arr = io.BytesIO()
            pil_image.save(img_byte_arr, format='JPEG', quality=95)
            img_bytes = img_byte_arr.getvalue()

            # 上传到图库
            image_url = zhipu_image_upload(img_bytes).get('result').get('file_url')

            # 图片向量化
            embedding = get_embedding(image_url)

            doc.close()

            return EmbedData(
                embedding=embedding,
                image_url=image_url,
                image_width=width,
                image_height=height,
                file_id=pdf_id,
                file_name=pdf_filename,
                file_page=page_num,
                file_url=pdf_url,
                knowledge_base_id=kb_id
            )

        except Exception as e:
            raise Exception(f"转换第 {page_num} 页失败: {str(e)} {traceback.format_exc()}")

    def _cleanup_temp_file(self, file_path: str):
        """清理临时文件"""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
        except:
            pass

    def cleanup_temp_images(self, image_paths: List[str]):
        """清理临时图片文件"""
        for path in image_paths:
            self._cleanup_temp_file(path)

    async def cleanup_all_temp_files(self, images_data: List[Dict[str, Any]]):
        """清理所有临时文件"""
        # 清理图片临时文件
        for img_data in images_data:
            if "image_path" in img_data:
                self._cleanup_temp_file(img_data["image_path"])

        # 注意：PDF临时文件已经在转换完成后立即清理

    def shutdown(self):
        """关闭线程池"""
        self.executor.shutdown(wait=True)
