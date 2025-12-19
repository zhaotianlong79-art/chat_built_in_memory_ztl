import asyncio
from typing import Optional

from src.third_party_service.jina import get_embeddings_async


async def embed_text(custom_input: Optional[list] = None):
    embed_data = await get_embeddings_async(custom_input=custom_input)
    return embed_data


async def main():
    print("=== 异步方法示例 ===")

    custom_input = [
        {
            "text": "海滩上美丽的日落"
        },
        {
            "text": "浜辺に沈む美しい夕日"
        },
        {
            "image": "https://i.ibb.co/nQNGqL0/beach1.jpg"
        },
    ]
    result3 = await embed_text(custom_input=custom_input)
    print(result3)


if __name__ == "__main__":
    # 运行异步示例
    asyncio.run(main())
