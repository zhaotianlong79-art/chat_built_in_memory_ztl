from pydantic import BaseModel, Field


class UserPromptParams(BaseModel):
    domain: str = Field(default="", description="domain of the chat session")
    skill: str = Field(default="", description="skill of the chat session")
    task_description: str = Field(default="", description="task description of the chat session")
    user_input: str = Field(default="", description="user input of the chat session")
    step_one: str = Field(default="", description="step one of the chat session")
    detailed_format_requirements: str = Field(default="", description="detailed format requirements of the chat session")
    notes: str = Field(default="", description="notes of the chat session")
    academic_document_processing_example: str = Field(default="", description="academic document processing example of the chat session")
    references: str = Field(default="", description="references of the chat session")
    # add other fields as needed


#
# USER_PROMPT_KEY_MAP = {
#     "domain":"",
#     "skill":"",
#     "task_escription":"",
#     "user_input":"",
#     "step_one":"",
#     "detailed_format_requirements":"",
#     "notes":"",
#     "academic_document_processing_example":"",
#     "references":""
# }