import asyncio
from typing import Optional

import httpx

from src.config.config import settings


async def get_embeddings_async(
        input_type: str = "text",
        content: Optional[str] = None,
        custom_input: Optional[list] = None
):
    """异步获取嵌入向量"""

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {settings.EMBED_SERVER_TOKEN}"
    }

    # 构建输入数据
    if custom_input is not None:
        # 使用自定义输入
        input_data = custom_input
    else:
        # 根据类型构建单个输入
        if input_type == "text":
            input_data = [{"text": content}]
        elif input_type == "image_url":
            input_data = [{"image": content}]
        elif input_type == "image_base64":
            input_data = [{"image": content}]
        else:
            raise ValueError("input_type 必须是 'text', 'image_url' 或 'image_base64'")

    # 请求数据
    data = {
        "model": "jina-embeddings-v4",
        "task": "text-matching",
        "input": input_data
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                settings.EMBED_SERVER_URL,
                headers=headers,
                json=data,
                timeout=30.0
            )

            response.raise_for_status()
            result = response.json()
            return result

        except httpx.HTTPStatusError as e:
            print(f"HTTP错误: {e.response.status_code}")
            print(f"错误信息: {e.response.text}")
            return None
        except httpx.RequestError as e:
            print(f"请求错误: {e}")
            return None
        except Exception as e:
            print(f"其他错误: {e}")
            return None


# 使用示例
async def main():
    print("=== 异步方法示例 ===")

    # 示例1: 处理文本
    print("1. 处理文本:")
    result1 = await get_embeddings_async(
        input_type="text",
        content="A beautiful sunset over the beach"
    )
    if result1:
        print(f"文本嵌入向量长度: {len(result1.get('data')[0].get('embedding'))}")

    # 示例2: 处理图片URL
    print("\n2. 处理图片URL:")
    result2 = await get_embeddings_async(
        input_type="image_url",
        content="https://i.ibb.co/nQNGqL0/beach1.jpg"  # 替换为实际URL
    )
    if result2:
        print(f"图片URL嵌入向量长度: {len(result1.get('data')[0].get('embedding'))}")



if __name__ == "__main__":
    # 运行异步示例
    asyncio.run(main())

