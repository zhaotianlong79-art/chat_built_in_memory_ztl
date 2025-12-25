import time
from dataclasses import dataclass
from typing import Dict, Any, Optional, List, Union, Set

from loguru import logger
from pymilvus import DataType
from pymilvus import MilvusClient, MilvusException

from src.config.config import settings


@dataclass
class MilvusConfig:
    """Milvus连接配置类"""
    host: str = settings.MILVUS_DB_HOST
    port: int = settings.MILVUS_DB_PORT
    db_name: str = settings.MILVUS_DB_NAME
    user: str = settings.MILVUS_DB_USER
    password: str = settings.MILVUS_DB_PASS
    timeout: int = settings.MILVUS_DB_TIMEOUT


class MilvusConnector:
    def __init__(self, config: Optional[MilvusConfig] = None):
        self._client: Optional[MilvusClient] = None
        self._connected: bool = False
        self.config = config or MilvusConfig()

    def connect(self) -> None:
        if self._connected:
            return

        milvus_url = f"http://{self.config.host}:{self.config.port}"
        try:
            self._client = MilvusClient(
                uri=milvus_url,
                db_name=self.config.db_name,
                timeout=self.config.timeout,
                user=self.config.user,
                password=self.config.password,
            )
            # 只做一次轻量验证
            self._client.list_collections()
            self._connected = True
            logger.info(f"Successfully connected to Milvus at {milvus_url}")
        except Exception:
            self._client = None
            self._connected = False
            logger.exception("Failed to connect to Milvus")
            raise

    @property
    def client(self) -> MilvusClient:
        if not self._connected:
            self.connect()
        return self._client


class MilvusClientWrapper:
    """Milvus 业务客户端，负责集合操作"""

    # 预定义集合字段 - 使用自动生成ID
    COLLECTION_FIELDS = [
        ("id", DataType.INT64, {"is_primary": True, "auto_id": True}),  # 改为自动生成ID
        ("embedding", DataType.FLOAT_VECTOR, {}),
        ("image_url", DataType.VARCHAR, {"max_length": 512}),
        ("image_width", DataType.INT64, {}),
        ("image_height", DataType.INT64, {}),
        ("file_id", DataType.VARCHAR, {"max_length": 100}),
        ("file_name", DataType.VARCHAR, {"max_length": 100}),
        ("file_page", DataType.INT64, {}),
        ("file_url", DataType.VARCHAR, {"max_length": 512}),
        ("knowledge_base_id", DataType.VARCHAR, {"max_length": 100}),
    ]

    def __init__(self, connector: MilvusConnector):
        self.connector = connector
        self.collection_name = ''
        self._loaded_collections: Set[str] = set()  # 缓存已加载的集合名称

    def _ensure_connected(self) -> None:
        """确保已建立连接"""
        self.connector.connect()

    def _wait_for_collection_load(self, collection_name: str, timeout: int = 30) -> None:
        """等待集合加载完成"""
        client = self.connector.client
        start_time = time.time()
        while True:
            if client.get_load_state(collection_name):
                logger.info(f"Collection {collection_name} loaded successfully in {time.time() - start_time}")
                return
            if time.time() - start_time > timeout:
                raise TimeoutError(f"Collection {collection_name} loading timeout")
            time.sleep(0.5)

    def ensure_collection(
            self,
            collection_name: str = settings.MILVUS_DB_COLLECTION_NAME,
            dimension: int = 2048,
            metric_type: str = settings.SEARCH_CONFIG['metric_type']
    ) -> None:
        """确保集合存在并已加载"""
        self._ensure_connected()
        client = self.connector.client
        self.collection_name = collection_name

        # 检查缓存并验证实际加载状态
        if collection_name in self._loaded_collections:
            if client.get_load_state(collection_name):
                logger.debug(f"Collection {collection_name} already loaded")
                return
            else:
                logger.warning(f"Collection {collection_name} in cache but not actually loaded")
                self._loaded_collections.remove(collection_name)

        try:
            if client.has_collection(collection_name):
                logger.info(f"Loading collection: {collection_name}")
                client.load_collection(collection_name)
                self._wait_for_collection_load(collection_name)
                self._loaded_collections.add(collection_name)
                return

            # 创建新集合
            logger.info(f"Creating new collection: {collection_name}")

            # 创建schema
            schema = client.create_schema(
                auto_id=True,
                enable_dynamic_field=True,
            )

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

            # 加载集合（必须先加载才能创建索引）
            logger.info(f"Loading new collection: {collection_name}")
            client.load_collection(collection_name)
            self._wait_for_collection_load(collection_name)

            # 创建向量索引
            index_params = client.prepare_index_params()
            index_params.add_index(
                field_name="embedding",
                metric_type=metric_type,
                index_type="HNSW",
                params={"M": 32, "efConstruction": 200}
            )
            client.create_index(
                collection_name=collection_name,
                index_params=index_params
            )

            # 为标量字段创建索引
            scalar_index_params = client.prepare_index_params()
            field_names = ["knowledge_base_id", "file_name"]
            for name in field_names:
                scalar_index_params.add_index(
                    field_name=name,
                    index_type="INVERTED"
                )

            client.create_index(
                collection_name=collection_name,
                index_params=scalar_index_params
            )

            logger.info(f"Collection {collection_name} created and indexed successfully")
            self._loaded_collections.add(collection_name)

        except MilvusException as e:
            logger.error(f"Milvus operation failed: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            raise

    def query(self, filter: str, output_fields: Optional[List[str]]) -> List[Dict[str, Any]]:
        self._ensure_connected()
        client = self.connector.client
        try:
            result = client.query(
                collection_name=self.collection_name,
                filter=filter,
                output_fields=output_fields
            )
            return result
        except MilvusException as e:
            logger.error(f"Milvus operation failed: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            raise

    def insert(self, data: Union[Dict[str, Any], List[Dict[str, Any]]]) -> List:
        """插入数据"""
        self._ensure_connected()
        client = self.connector.client

        try:
            if isinstance(data, dict):
                data = [data]

            # 验证数据格式
            for item in data:
                if "embedding" not in item:
                    raise ValueError("Data item is missing 'embedding' field")
                if not isinstance(item["embedding"], list) or len(item["embedding"]) == 0:
                    raise ValueError("Embedding must be a non-empty list")

                # 移除用户可能提供的ID（因为auto_id=True）
                if "id" in item:
                    logger.warning("Removing user-provided ID as auto_id=True")
                    del item["id"]

            # 使用原始数据（动态字段支持）
            result = client.insert(self.collection_name, data)
            logger.info(f"Successfully inserted {len(result['ids'])} records into {self.collection_name}")
            return result['ids']
        except MilvusException as e:
            logger.error(f"Failed to insert data: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            raise

    def search(
            self,
            query_vectors: List[List[float]],
            search_params: Dict[str, Any],
            limit: int = 10,
            output_fields: Optional[List[str]] = None,
            collection_name: Optional[str] = None,
            filter: Optional[str] = None
    ) -> list[list[dict]]:

        self._ensure_connected()
        client = self.connector.client
        collection_name = collection_name or self.collection_name

        try:
            if not query_vectors:
                raise ValueError("Query vectors cannot be empty")
            if not isinstance(query_vectors[0], list) or not query_vectors[0]:
                raise ValueError("Query vectors must be non-empty lists")

            # 确保集合已加载
            if collection_name not in self._loaded_collections:
                self.ensure_collection(collection_name)

            # 设置默认搜索参数
            default_params = {"metric_type": "L2", "params": {"nprobe": 10}}
            merged_params = {**default_params, **(search_params or {})}

            results = client.search(
                collection_name=collection_name,
                data=query_vectors,
                anns_field="embedding",
                search_params=merged_params,
                limit=limit,
                output_fields=output_fields or [],
                filter=filter
            )
            logger.info(f"Search returned {len(results[0])} results")
            return results
        except MilvusException as e:
            logger.error(f"Search failed: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            raise


_milvus_client: Optional[MilvusClientWrapper] = None


def get_milvus_client() -> MilvusClientWrapper:
    global _milvus_client
    if _milvus_client is None:
        config = MilvusConfig()
        connector = MilvusConnector(config)
        _milvus_client = MilvusClientWrapper(connector)
    return _milvus_client
