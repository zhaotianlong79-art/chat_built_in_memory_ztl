from typing import List

from src.third_party_service.jina import get_embeddings_async


async def embed_text(custom_input: List[str]):
    embed_data = await get_embeddings_async(custom_input=custom_input)
    return embed_data.get('data')[0].get('embedding')
