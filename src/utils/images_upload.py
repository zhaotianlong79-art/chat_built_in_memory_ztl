import asyncio
import tempfile
import traceback
from abc import ABC, abstractmethod
import time
from typing import Dict, Any, Optional

import requests
from loguru import logger

from src.config.config import settings
from src.service.embed_service import embed_text


def generate_temp_filename(suffix='.jpg'):
    # 生成带有指定后缀的临时文件名
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    filename = temp_file.name
    temp_file.close()
    return filename


class FileUploader(ABC):
    """文件上传器抽象基类"""

    @abstractmethod
    def upload(self, file_content: bytes, file_type: str, file_name: Optional[str] = None) -> Dict[str, Any]:
        """上传文件的抽象方法"""
        pass


class ZhiPuFileUploader(FileUploader):
    """智谱AI文件上传器实现"""

    def __init__(self, api_key: str = None):
        pass

    def upload(self, file_content: bytes, file_type: str, file_name: Optional[str] = None) -> Dict[str, Any]:
        """实现文件上传接口"""
        if not file_name:
            file_name = generate_temp_filename()

        method = "post"
        files = {
            "file": (file_name, file_content, "image/{}".format(file_type))
        }
        response = getattr(requests, method)(url=settings.IMAGE_UPLOAD_SERVE, files=files)
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Upload failed with status code {response.status_code}: {response.text}")


class FileUploaderFactory:
    """文件上传器工厂类"""

    _uploaders = {
        'zhipu': ZhiPuFileUploader
    }

    @classmethod
    def create_uploader(cls, uploader_type: str, **kwargs) -> FileUploader:
        """创建文件上传器实例"""
        if uploader_type not in cls._uploaders:
            raise ValueError(f"Unknown uploader type: {uploader_type}")

        uploader_class = cls._uploaders[uploader_type]
        return uploader_class(**kwargs)

    @classmethod
    def register_uploader(cls, name: str, uploader_class: type):
        """注册新的文件上传器类型"""
        if not issubclass(uploader_class, FileUploader):
            raise TypeError("Uploader class must be a subclass of FileUploader")
        cls._uploaders[name] = uploader_class


def zhipu_image_upload(image_data: bytes) -> Optional[Dict[str, Any]]:
    # 创建智谱上传器实例
    uploader = FileUploaderFactory.create_uploader('zhipu')

    try:
        # 上传文件（不指定文件名，将使用临时文件名）
        result = uploader.upload(
            file_content=image_data,
            file_type='jpg'  # 文件类型/扩展名
        )
        return result
    except Exception as e:
        logger.error(f"upload images data error: {traceback.format_exc()}")
        return None


async def test(image_url: str):
    custom_input = [
        {"image": image_url}
    ]
    embedding = await embed_text(custom_input=custom_input)
    return embedding[0].get("embedding")


def main():
    with open(r'C:\Users\zhaokunming\Pictures\Saved Pictures\beach2.jpg', 'rb') as f:
        image_data = f.read()
    image_url = zhipu_image_upload(image_data).get('result').get('file_url')
    result = asyncio.run(test(image_url))
    print(result)


if __name__ == '__main__':
    start = time.time()
    main()
    print(start - time.time())
