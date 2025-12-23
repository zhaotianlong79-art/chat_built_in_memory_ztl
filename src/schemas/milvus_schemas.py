from typing import List

from pydantic import BaseModel, Field


class EmbedData(BaseModel):
    embedding: List[float] = Field(default=[], description="embedding 向量数据")
    image_url: str = Field(default="", description="图片地址")
    image_width: int = Field(description="图片宽度")
    image_height: int = Field(description="图片长度")
    file_id: str = Field(default="", description="所属文件id")
    file_name: str = Field(default="", description="所属文件名字")
    file_page: int = Field(description="图片所属文件的页码")
    file_url: str = Field(default="", description="所属文件地址")
    knowledge_base_id: str = Field(default="", description="知识库id")

    def to_json(self, indent: int = None) -> str:
        """
        将对象转换为 JSON 字符串
        """
        return self.model_dump_json(indent=indent)

    def to_dict(self) -> dict:
        """
        将对象转换为字典
        """
        return self.model_dump()

    @classmethod
    def from_json(cls, json_str: str) -> 'EmbedData':
        """
        从 JSON 字符串创建 EmbedData 实例
        """
        return cls.model_validate_json(json_str)



