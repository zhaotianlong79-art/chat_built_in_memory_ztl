import math
from typing import Optional

from fastapi import Query, HTTPException
from mongoengine.queryset.visitor import Q

from src.models.mongo import KnowledgeBase, Files


async def get_knowledge_bases(
        page: int = Query(1, description="页码", ge=1),
        page_size: int = Query(10, description="每页数量", ge=1, le=100),
        knowledge_name: Optional[str] = Query(None, description="知识库名称（模糊查询）"),
        order_by: str = Query("-created_at", description="排序字段，-表示降序，+表示升序")
):
    """分页查询知识库"""
    try:
        # 构建查询条件
        query = Q()

        if knowledge_name:
            # 模糊查询，不区分大小写
            query &= Q(knowledge_name__icontains=knowledge_name)

        # 获取总数
        total = KnowledgeBase.objects(query).count()

        # 计算总页数
        total_pages = math.ceil(total / page_size) if total > 0 else 0

        # 处理排序
        sort_field = order_by
        if order_by.startswith("-"):
            sort_field = f"-{order_by[1:]}"

        # 分页查询
        skip_count = (page - 1) * page_size
        knowledge_bases = KnowledgeBase.objects(query) \
            .order_by(sort_field) \
            .skip(skip_count) \
            .limit(page_size)

        # 序列化数据
        items = []
        for kb in knowledge_bases:
            # 获取每个知识库的文件数量
            file_count = Files.objects(knowledge_base_id=str(kb.id)).count()

            items.append({
                "id": str(kb.id),
                "knowledge_name": kb.knowledge_name,
                "knowledge_description": kb.knowledge_description,
                "file_count": file_count,
                "created_at": kb.created_at.isoformat() if hasattr(kb, 'created_at') else None,
                "updated_at": kb.updated_at.isoformat() if hasattr(kb, 'updated_at') else None
            })

        return {
            "items": items,
            "pagination": {
                "page": page,
                "page_size": page_size,
                "total": total,
                "total_pages": total_pages,
                "has_previous": page > 1,
                "has_next": page < total_pages
            }
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"查询失败: {str(e)}")


async def get_knowledge_file(
        knowledge_base_id: str = Query(..., description="知识库ID"),
        page: int = Query(1, description="页码", ge=1),
        page_size: int = Query(10, description="每页数量", ge=1, le=100),
        file_name: Optional[str] = Query(None, description="文件名（模糊查询）"),
        file_type: Optional[str] = Query(None, description="文件类型"),
        order_by: str = Query("-created_at", description="排序字段，-表示降序，+表示升序")
):
    """分页查询知识库的包含的文件"""
    try:
        # 首先验证知识库是否存在
        knowledge_base = KnowledgeBase.objects(id=knowledge_base_id).first()
        if not knowledge_base:
            raise HTTPException(status_code=404, detail="知识库不存在")

        # 构建查询条件
        query = Q(knowledge_base_id=knowledge_base_id)

        if file_name:
            query &= Q(file_name__icontains=file_name)

        if file_type:
            query &= Q(file_type=file_type)

        # 获取总数
        total = Files.objects(query).count()

        # 计算总页数
        total_pages = math.ceil(total / page_size) if total > 0 else 0

        # 处理排序
        sort_field = order_by
        if order_by.startswith("-"):
            sort_field = f"-{order_by[1:]}"
        elif order_by.startswith("+"):
            sort_field = order_by[1:]

        # 分页查询
        skip_count = (page - 1) * page_size
        files = Files.objects(query) \
            .order_by(sort_field) \
            .skip(skip_count) \
            .limit(page_size)

        # 序列化数据
        items = []
        for file in files:
            items.append({
                "id": str(file.id),
                "file_name": file.file_name,
                "file_size": file.file_size,
                "file_url": file.file_url,
                "file_type": file.file_type,
                "knowledge_base_id": file.knowledge_base_id,
                "knowledge_base_name": knowledge_base.knowledge_name,
                "created_at": file.created_at.isoformat() if hasattr(file, 'created_at') else None,
                "updated_at": file.updated_at.isoformat() if hasattr(file, 'updated_at') else None
            })

        return {
            "knowledge_base": {
                "id": str(knowledge_base.id),
                "name": knowledge_base.knowledge_name,
                "description": knowledge_base.knowledge_description
            },
            "items": items,
            "pagination": {
                "page": page,
                "page_size": page_size,
                "total": total,
                "total_pages": total_pages,
                "has_previous": page > 1,
                "has_next": page < total_pages
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"查询失败: {str(e)}")


# 如果你还需要一个更简单的版本，这里是一个基本版本：
async def get_knowledge_bases_simple(
        page: int = 1,
        page_size: int = 10
):
    """简单分页查询知识库"""
    try:
        skip_count = (page - 1) * page_size

        # 查询数据
        knowledge_bases = KnowledgeBase.objects() \
            .skip(skip_count) \
            .limit(page_size)

        # 获取总数
        total = KnowledgeBase.objects().count()

        items = []
        for kb in knowledge_bases:
            items.append({
                "id": str(kb.id),
                "knowledge_name": kb.knowledge_name,
                "knowledge_description": kb.knowledge_description
            })

        return {
            "items": items,
            "page": page,
            "page_size": page_size,
            "total": total
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"查询失败: {str(e)}")


async def get_knowledge_file_simple(
        knowledge_base_id: str,
        page: int = 1,
        page_size: int = 10
):
    """简单分页查询知识库文件"""
    try:
        skip_count = (page - 1) * page_size

        # 查询数据
        files = Files.objects(knowledge_base_id=knowledge_base_id) \
            .skip(skip_count) \
            .limit(page_size)

        # 获取总数
        total = Files.objects(knowledge_base_id=knowledge_base_id).count()

        items = []
        for file in files:
            items.append({
                "id": str(file.id),
                "file_name": file.file_name,
                "file_size": file.file_size,
                "file_url": file.file_url,
                "file_type": file.file_type
            })

        return {
            "items": items,
            "page": page,
            "page_size": page_size,
            "total": total
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"查询失败: {str(e)}")
