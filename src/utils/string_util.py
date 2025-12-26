from src.schemas.prompt_schemas import UserPromptParams
from src.service.prompt.chat_prompt import USER_PROMPT


def replace_key_by_map(string: str, key_value_map: dict) -> str:
    new_string = string
    for key, value in key_value_map.items():
        new_string = new_string.replace(key, value)

    return new_string


def get_default_user_prompt(string: UserPromptParams, prompt=USER_PROMPT) -> str:
    USER_PROMPT_KEY_MAP = {
        "domain": UserPromptParams.domain,
        "skill": UserPromptParams.skill,
        "task_escription": UserPromptParams.task_description,
        "user_input": UserPromptParams.user_input,
        "step_one": UserPromptParams.step_one,
        "detailed_format_requirements": UserPromptParams.detailed_format_requirements,
        "notes": UserPromptParams.notes,
        "academic_document_processing_example": UserPromptParams.academic_document_processing_example,
        "references": UserPromptParams.references
    }
    return replace_key_by_map(prompt, USER_PROMPT_KEY_MAP)
