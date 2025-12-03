import datetime
import traceback

from bson import ObjectId
from mongoengine import Document, DateTimeField, StringField, DictField, ListField

from src.db_conn.mongo import init_mongo_db, close_mongo_db


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


# chat_history
class ChatHistory(BaseDocument):
    meta = {
        'collection': 'chat_history',  # 映射到数据库 document_classify_task 集合
        'indexes': ['session_id'],
    }
    session_id = StringField()  # 会话id
    user_id = StringField()  # 用户id
    messages = ListField(DictField())  # 消息列表

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


def create_chat_history(
        session_id,
        user_id=None,
        messages=None
):
    # 创建新的任务记录
    task = ChatHistory(
        session_id=session_id,
        user_id=user_id,
        messages=messages
    )

    # 保存到数据库
    task.save()
    return task


# 使用示例
def main():
    try:
        # 初始化数据库连接
        init_mongo_db()

        # 创建任务
        task = create_chat_history(
            session_id="1234567890",
            user_id="user123",
            messages=[{"role": "user", "content": "你好"},
                      {"role": "assistant", "content": "你好，有什么可以帮助你的吗？"}]
        )

        print(f"成功创建任务，ID: {task.id}")

    except Exception as e:
        print(f"发生错误: {str(e)} {traceback.format_exception()}")
    finally:
        # 确保关闭数据库连接
        close_mongo_db()


if __name__ == "__main__":
    main()
