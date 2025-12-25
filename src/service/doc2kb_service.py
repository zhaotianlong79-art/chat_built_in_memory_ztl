import asyncio
import io
import os
import tempfile
import time
import traceback
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Any

import fitz  # PyMuPDF
from PIL import Image
from fastapi import UploadFile, HTTPException
from loguru import logger

from src.config.config import settings
from src.repositories.file_repository import create_file_data
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


def truncate_filename(filename, max_length=25):
    """milvus使用字节长度，一个中文是三字节25*3=75"""
    filename = filename[8:]  # 去掉前缀的随机生产的uid
    if len(filename) > max_length:
        # 保留扩展名，截断主体部分
        name, ext = os.path.splitext(filename)
        truncated_name = name[:max_length - len(ext) - 1]  # -1 用于省略号
        return f"{truncated_name}...{ext}"
    return filename


class PDFToImageService:
    def __init__(self):
        self.executor = ThreadPoolExecutor(max_workers=settings.IMAGE_MAX_WORKERS)

    # 使用上下文管理器确保资源正确释放
    async def convert_pdf_to_images(
            self,
            pdf_file: UploadFile,
            knowledge_base_id: str,
            pages: List[int] = None
    ) -> List[Dict[str, Any]]:
        """将PDF文件转换为图片列表"""

        # 验证文件类型
        if not pdf_file.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="文件必须是PDF格式")

        temp_pdf_path = None
        try:
            # 创建临时文件保存PDF
            temp_pdf_path = self._save_temp_pdf(pdf_file)

            # 并发处理PDF转换
            images_data = await self._process_pdf_concurrent(
                temp_pdf_path,
                pages,
                pdf_file.filename,
                knowledge_base_id
            )

            return images_data

        except Exception as e:
            logger.error(f"PDF转换失败: {traceback.format_exc()}")
            raise HTTPException(status_code=500, detail=f"PDF转换失败: {str(e)}")
        finally:
            # 确保临时文件被清理
            if temp_pdf_path and os.path.exists(temp_pdf_path):
                self._cleanup_temp_file(temp_pdf_path)

    def _save_temp_pdf(self, pdf_file: UploadFile) -> str:
        """保存PDF到临时文件"""
        # 使用tempfile创建临时文件，避免手动管理文件名
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
            # 读取并保存PDF文件
            content = pdf_file.file.read()
            tmp.write(content)
            return tmp.name

    async def _process_pdf_concurrent(
            self,
            pdf_path: str,
            pages: List[int],
            pdf_filename: str,
            knowledge_base_id: str
    ) -> List[Dict[str, Any]]:
        """并发处理PDF转换"""
        start_time = time.time()
        logger.info(f"开始转换为知识库，文件：{pdf_filename}")

        try:
            # 一次性打开PDF文件获取所有信息
            with fitz.open(pdf_path) as doc:
                total_pages = doc.page_count

                # 确定要转换的页码
                if pages is None:
                    pages_to_convert = list(range(1, total_pages + 1))
                else:
                    # 验证页码有效性
                    pages_to_convert = []
                    invalid_pages = []
                    for page_num in pages:
                        if 1 <= page_num <= total_pages:
                            pages_to_convert.append(page_num)
                        else:
                            invalid_pages.append(str(page_num))

                    if invalid_pages:
                        raise HTTPException(
                            status_code=400,
                            detail=f"页码 {', '.join(invalid_pages)} 超出范围 (1-{total_pages})"
                        )
        except Exception as e:
            logger.error(f"打开PDF文件失败: {str(e)}")
            raise

        # 记录文件信息（可以考虑异步化）
        try:
            await create_file_data(
                file_name=pdf_filename,
                file_size=str(os.path.getsize(pdf_path)) + "（bytes）",
                file_url="file_url",
                file_type=os.path.splitext(pdf_filename)[1],
                knowledge_base_id=knowledge_base_id,
            )
        except Exception as e:
            logger.warning(f"记录文件数据失败: {str(e)}")
            # 不要因为记录失败而影响主流程

        # 批量提交任务，避免循环中重复创建future
        futures = [
            self.executor.submit(
                self._convert_single_page,
                pdf_path,
                page_num,
                pdf_filename,
                "pdf_id",  # 需要从外部传入
                "pdf_url",  # 需要从外部传入
                knowledge_base_id,
                settings.IMAGE_DPI
            )
            for page_num in pages_to_convert
        ]

        # 收集结果并处理异常
        images_data = []
        failed_pages = []

        for future in as_completed(futures):
            try:
                result = future.result()
                images_data.append(result)
            except Exception as e:
                # 记录失败页面但继续处理其他页面
                logger.error(f"页面转换失败: {str(e)}")
                failed_pages.append(str(futures.index(future) + 1))

        # 如果有页面失败，记录日志但不中断流程
        if failed_pages:
            logger.warning(f"以下页码转换失败: {', '.join(failed_pages)}")

        # 按页码排序
        # images_data.sort(key=lambda x: x.get("file_page", 0))

        end_time = time.time()
        logger.info(
            f"知识库转换完成，文件：{pdf_filename}，总页数：{len(images_data)}，失败页数：{len(failed_pages)}，处理时间：{end_time - start_time:.2f}秒")

        return images_data

    def _convert_single_page(
            self,
            pdf_path: str,
            page_num: int,
            pdf_filename: str,
            pdf_id: str,
            pdf_url: str,
            kb_id: str,
            dpi: int = settings.IMAGE_DPI,
    ) -> Dict:
        """转换单个PDF页面为图片"""
        try:
            # 使用上下文管理器确保PDF文件正确关闭
            with fitz.open(pdf_path) as doc:
                page = doc.load_page(page_num - 1)

                # 计算缩放比例
                zoom = dpi / 72
                mat = fitz.Matrix(zoom, zoom)

                # 直接渲染为Pixmap，避免中间转换
                pix = page.get_pixmap(matrix=mat, alpha=False, dpi=dpi)

                # 直接保存为JPEG格式，避免PIL转换
                img_byte_arr = io.BytesIO()

                # 检查是否需要使用PIL进行额外处理
                if hasattr(pix, 'pil_save'):
                    # 如果有pil_save方法，直接使用
                    pil_image = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                    pil_image.save(img_byte_arr, format='JPEG', quality=95)
                else:
                    # 否则使用默认方式
                    pil_image = Image.open(io.BytesIO(pix.tobytes("ppm")))
                    pil_image.save(img_byte_arr, format='JPEG', quality=95)

                img_bytes = img_byte_arr.getvalue()

                # 图片上传和向量化（考虑是否需要异步处理）
                upload_result = zhipu_image_upload(img_bytes)
                if not upload_result or 'result' not in upload_result:
                    raise Exception("图片上传失败")

                image_url = upload_result['result'].get('file_url')

                # 获取向量嵌入
                embedding = get_embedding(image_url)

                return EmbedData(
                    embedding=embedding,
                    image_url=image_url,
                    image_width=pix.width,
                    image_height=pix.height,
                    file_id=pdf_id,
                    file_name=truncate_filename(pdf_filename),
                    file_page=page_num,
                    file_url=pdf_url,
                    knowledge_base_id=kb_id
                ).to_dict()

        except Exception as e:
            logger.error(f"转换第 {page_num} 页失败: {str(e)}")
            raise Exception(f"转换第 {page_num} 页失败: {str(e)}")

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
