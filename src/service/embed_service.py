from src.third_party_service.jina import get_embeddings_async


async def embed_text(_type: str = "text", text: str = ''):
    embed_data = await get_embeddings_async(_type, text)
    return embed_data.get('data')[0].get('embedding')


async def embed_image(_type: str = "image_url", image_url: str = ''):
    embed_data = await get_embeddings_async(_type, image_url)
    return embed_data.get('data')[0].get('embedding')
