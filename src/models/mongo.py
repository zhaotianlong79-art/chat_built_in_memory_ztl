import datetime

from bson import ObjectId
from mongoengine import Document, DateTimeField, StringField, ListField


class BaseDocument(Document):
    meta = {
        'abstract': True,
    }

    create_time = DateTimeField()  # 创建时间
    update_time = DateTimeField()  # 修改时间

    def save(self, *args, **kwargs):
        if not self.create_time:
            self.create_time = datetime.datetime.now()
        self.update_time = datetime.datetime.now()
        return super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """
        硬删除方法，从数据库中永久删除记录
        """
        return super().delete(*args, **kwargs)

    def to_dict(self):
        """将MongoEngine文档对象转换为可序列化的字典"""
        data = self.to_mongo().to_dict()

        # 处理ObjectId类型，转换为字符串
        if '_id' in data:
            data['_id'] = str(data['_id'])

        # 处理其他可能存在的ObjectId字段
        for key, value in data.items():
            if isinstance(value, ObjectId):
                data[key] = str(value)

        return data

    @classmethod
    def from_dict(cls, data):
        """从字典重建对象（如果需要的话）"""
        # 处理_id字段的转换
        if '_id' in data and isinstance(data['_id'], str):
            try:
                data['_id'] = ObjectId(data['_id'])
            except:
                pass
        return cls(**data)


# chat_history
class ChatHistory(BaseDocument):
    meta = {
        'collection': 'chat_history',  # 映射到数据库 chat_history 集合
        'indexes': ['session_id'],
    }
    session_id = StringField()  # 会话id
    user_id = StringField()  # 用户id
    messages = ListField(default=list)  # 消息列表


class KnowledgeBase(BaseDocument):
    meta = {
        'collection': 'knowledge_base',  # 映射到数据库 knowledge_base 集合
        'indexes': ['knowledge_name'],
    }
    knowledge_name = StringField()  # 知识库名称
    knowledge_description = StringField()  # 知识库描述


class Files(BaseDocument):
    meta = {
        'collection': 'files',  # 映射到数据库 files 集合
        'indexes': ['knowledge_base_id'],
    }
    file_name = StringField()  # 文件名
    file_size = StringField()  # 文件大小
    file_url = StringField()  # 文件url
    file_type = StringField()  # 文件类型
    knowledge_base_id = StringField()  # 知识库id
