from pydantic import BaseModel, Field


class CreateKnowledgeBaseParams(BaseModel):
    knowledge_base_name: str = Field(default="", description="知识库名字")
    knowledge_description: str = Field(default="", description="知识库描述")


class UpdateKnowledgeBaseParams(BaseModel):
    knowledge_base_id: str = Field(default="", description="知识库ID")
    knowledge_base_name: str = Field(default="", description="知识库名字")
    knowledge_description: str = Field(default="", description="知识库描述")


class SelectKnowledgeBaseParams(BaseModel):
    page: int = Field(default=1, description="知识库ID")
    page_size: int = Field(default=10, description="知识库ID")
    knowledge_name: str = Field(default="", description="知识库名称（模糊查询）")
    order_by: str = Field(default="", description="排序字段，-表示降序，+表示升序")


class SelectKnowledgeBaseFilesParams(BaseModel):
    knowledge_base_id: str = Field(default="", description="知识库ID")
    page: int = Field(default=1, description="页码")
    page_size: int = Field(default=10, description="每页数量")
    file_name: str = Field(default="", description="文件名（模糊查询）")
    file_type: str = Field(default="", description="文件类型")
    order_by: str = Field(default="", description="排序字段，-表示降序，+表示升序")
