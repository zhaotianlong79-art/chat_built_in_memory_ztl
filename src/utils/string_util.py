from src.schemas.prompt_schemas import UserPromptParams
from src.service.prompt.chat_prompt import USER_PROMPT


def replace_key_by_map(string: str, key_value_map: dict) -> str:
    new_string = string
    for key, value in key_value_map.items():
        new_string = new_string.replace(key, value)

    return new_string


def get_default_user_prompt(string: UserPromptParams, prompt=USER_PROMPT) -> str:
    USER_PROMPT_KEY_MAP = {
        "domain": string.domain,
        "skill": string.skill,
        "task_escription": string.task_description,
        "user_input": string.user_input,
        "step_one": string.step_one,
        "detailed_format_requirements": string.detailed_format_requirements,
        "notes": string.notes,
        "academic_document_processing_example": string.academic_document_processing_example,
        "references": string.references
    }
    return replace_key_by_map(prompt, USER_PROMPT_KEY_MAP)
