from pydantic import BaseModel, Field


class CreateKnowledgeBaseParams(BaseModel):
    knowledge_base_name: str = Field(default="", description="知识库名字")
    knowledge_description: str = Field(default="", description="知识库描述")

class UpdateKnowledgeBaseParams(BaseModel):
    knowledge_base_id: str = Field(default="", description="知识库ID")
    knowledge_base_name: str = Field(default="", description="知识库名字")
    knowledge_description: str = Field(default="", description="知识库描述")
