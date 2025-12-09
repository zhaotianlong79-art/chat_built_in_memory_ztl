import asyncio
from typing import Optional
from loguru import logger
import httpx

from src.config.config import settings


async def get_embeddings_async(custom_input: Optional[list] = None):
    """异步获取嵌入向量

    Args:
        custom_input: 包含文本或图像的输入列表，每个元素应包含'text'或'image'字段

    Returns:
        包含嵌入向量的字典列表，每个字典包含'index'、'image_or_text'和'embedding'字段
        发生错误时返回None
    """
    if not custom_input:
        logger.error("输入数据为空")
        return None

    # 验证输入格式
    for item in custom_input:
        if not isinstance(item, dict) or ("text" not in item and "image" not in item):
            logger.error("输入数据格式不正确，每个元素必须是包含'text'或'image'的字典")
            return None

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {settings.EMBED_SERVER_TOKEN}"
    }

    # 构建请求数据
    request_data = {
        "model": "jina-embeddings-v4",
        "task": "text-matching",
        "input": custom_input
    }


    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                settings.EMBED_SERVER_URL,
                headers=headers,
                json=request_data,
                timeout=30.0  # 从配置中读取
            )

            response.raise_for_status()
            response_data = response.json().get("data", [])

            # 构建结果
            results = []
            for item, embedding_data in zip(custom_input, response_data):
                results.append({
                    'index': item.get("text"),
                    "image_or_text": item.get("image") or item.get("text"),
                    'embedding': embedding_data.get("embedding"),
                })

            return results

        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP错误: {e.response.status_code}")
            logger.error(f"错误信息: {e.response.text}")
            return None
        except httpx.RequestError as e:
            logger.error(f"请求错误: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"未知错误: {str(e)}")
            return None


# 使用示例
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
    result3 = await get_embeddings_async(custom_input=custom_input)
    print(result3)


if __name__ == "__main__":
    # 运行异步示例
    asyncio.run(main())
