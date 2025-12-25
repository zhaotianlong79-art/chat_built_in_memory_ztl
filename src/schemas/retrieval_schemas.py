from typing import List

from pydantic import BaseModel, Field


class SearchDocumentImagesParams(BaseModel):
    query: str = Field(default="", description="检索问题")
    knowledge_base_id: str = Field(default="", description="知识库id")
    file_ids: List[str] = Field(default=[], description="指定文件id")
    min_similarity: float = Field(default=0.6, description="相似度阈值")
    limit: int = Field(default=10, description="获取多少个")
