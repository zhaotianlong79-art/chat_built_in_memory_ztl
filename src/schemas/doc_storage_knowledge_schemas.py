from typing import List

from pydantic import BaseModel, Field


class DocKnowledgeBase(BaseModel):
    file_urls: List[str] = Field(default=[], description="File URLs")
