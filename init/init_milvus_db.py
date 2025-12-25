#!/usr/bin/env python3
"""
独立的 Milvus 集合创建脚本（强制重建模式）
"""

from loguru import logger

from pymilvus import DataType, MilvusException

from src.config.config import settings
from src.db_conn.milvus import MilvusConnector


class CollectionCreator:
    """独立的集合创建器（支持强制重建）"""

    # 预定义集合字段
    COLLECTION_FIELDS = [
        ("id", DataType.INT64, {"is_primary": True, "auto_id": True}),  # 改为自动生成ID
        ("embedding", DataType.FLOAT_VECTOR, {}),
        ("image_url", DataType.VARCHAR, {"max_length": 512}),
        ("image_width", DataType.INT64, {}),
        ("image_height", DataType.INT64, {}),
        ("file_id", DataType.INT64, {}),
        ("file_name", DataType.VARCHAR, {"max_length": 100}),
        ("file_page", DataType.INT64, {}),
        ("file_url", DataType.INT64, {}),
        ("knowledge_base_id", DataType.VARCHAR, {"max_length": 100}),
    ]

    def __init__(self, connector: MilvusConnector):
        self.connector = connector

    def recreate_collection(
            self,
            collection_name: str = "colqwen_v1_0",
            dimension: int = 2048,
            metric_type: str = settings.SEARCH_CONFIG['metric_type'],
            force_recreate: bool = True
    ) -> bool:
        """
        重建集合（如果存在则先删除）

        Args:
            collection_name: 集合名称
            dimension: 向量维度
            metric_type: 相似度度量类型 (IP/L2等)
            force_recreate: 即使集合不存在也创建

        Returns:
            bool: True表示创建了新集合，False表示集合已存在且未重建
        """
        self.connector.connect()
        client = self.connector.client

        try:
            # 检查集合是否存在
            collection_exists = client.has_collection(collection_name)

            if collection_exists:
                logger.warning(f"Collection {collection_name} already exists, dropping...")
                client.drop_collection(collection_name)
                logger.success(f"Collection {collection_name} dropped successfully")
            elif not force_recreate:
                logger.info(f"Collection {collection_name} does not exist and force_recreate=False")
                return False

            # 创建新集合
            logger.info(f"Creating new collection: {collection_name}")

            # 创建schema
            schema = client.create_schema(auto_id=True, enable_dynamic_field=True)

            # 添加所有预定义字段
            for field_name, datatype, kwargs in self.COLLECTION_FIELDS:
                if field_name == "embedding":
                    kwargs["dim"] = dimension
                schema.add_field(field_name=field_name, datatype=datatype, **kwargs)

            # 创建集合
            client.create_collection(
                collection_name=collection_name,
                schema=schema,
                consistency_level="Strong"
            )

            # 创建索引
            self._create_indexes(collection_name, dimension, metric_type)

            logger.success(f"Collection {collection_name} created successfully")
            return True

        except MilvusException as e:
            logger.error(f"Milvus operation failed: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            raise

    def _create_indexes(self, collection_name: str, dimension: int, metric_type: str="IP") -> None:
        """创建向量和标量索引"""
        client = self.connector.client

        # 向量索引 (HNSW)
        vector_index_params = client.prepare_index_params()
        vector_index_params.add_index(
            field_name="embedding",
            metric_type=metric_type,
            index_type="HNSW",
            params={"M": 32, "efConstruction": 200}
        )
        client.create_index(collection_name, vector_index_params)
        logger.info("Vector index (HNSW) created")

        # 标量索引 (INVERTED)
        scalar_index_params = client.prepare_index_params()
        for field_name in ["knowledge_base_id", "file_name"]:
            scalar_index_params.add_index(
                field_name=field_name,
                index_type="INVERTED"
            )
        client.create_index(collection_name, scalar_index_params)
        logger.info("Scalar indexes (INVERTED) created")


def main():
    """主函数：强制重建集合"""
    from src.db_conn.milvus import MilvusConfig

    # 配置连接参数
    config = MilvusConfig(
        host=settings.MILVUS_DB_HOST,
        port=settings.MILVUS_DB_PORT,
        db_name=settings.MILVUS_DB_NAME,
        user=settings.MILVUS_DB_USER,
        password=settings.MILVUS_DB_PASS,
        timeout=settings.MILVUS_DB_TIMEOUT
    )

    # 创建连接器和集合创建器
    connector = MilvusConnector(config)
    creator = CollectionCreator(connector)

    try:
        # 强制重建集合
        success = creator.recreate_collection(
            collection_name=settings.MILVUS_DB_COLLECTION_NAME,
            dimension=2048,
            metric_type=settings.SEARCH_CONFIG['metric_type'],
            force_recreate=True
        )

        if success:
            print("Collection recreation completed successfully")
        else:
            print("Collection already exists and was not recreated")
        return 0

    except Exception as e:
        print(f"Collection recreation failed: {e}")
        return 1


if __name__ == "__main__":
    exit(main())
