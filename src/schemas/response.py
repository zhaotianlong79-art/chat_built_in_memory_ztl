from enum import Enum
from typing import Any, Optional, Dict, List, Generic, TypeVar

from fastapi import status
from pydantic import BaseModel, Field

T = TypeVar('T')


class ResponseCode(Enum):
    """响应状态码枚举（基于HTTP状态码扩展）"""
    SUCCESS = status.HTTP_200_OK
    CREATED = status.HTTP_201_CREATED
    ACCEPTED = status.HTTP_202_ACCEPTED
    NO_CONTENT = status.HTTP_204_NO_CONTENT

    # 客户端错误
    BAD_REQUEST = status.HTTP_400_BAD_REQUEST
    UNAUTHORIZED = status.HTTP_401_UNAUTHORIZED
    FORBIDDEN = status.HTTP_403_FORBIDDEN
    NOT_FOUND = status.HTTP_404_NOT_FOUND
    METHOD_NOT_ALLOWED = status.HTTP_405_METHOD_NOT_ALLOWED
    CONFLICT = status.HTTP_409_CONFLICT
    UNPROCESSABLE_ENTITY = status.HTTP_422_UNPROCESSABLE_ENTITY
    TOO_MANY_REQUESTS = status.HTTP_429_TOO_MANY_REQUESTS

    # 服务器错误
    INTERNAL_SERVER_ERROR = status.HTTP_500_INTERNAL_SERVER_ERROR
    NOT_IMPLEMENTED = status.HTTP_501_NOT_IMPLEMENTED
    BAD_GATEWAY = status.HTTP_502_BAD_GATEWAY
    SERVICE_UNAVAILABLE = status.HTTP_503_SERVICE_UNAVAILABLE
    GATEWAY_TIMEOUT = status.HTTP_504_GATEWAY_TIMEOUT


class BaseResponse(BaseModel, Generic[T]):
    """基础响应模型"""
    code: int = Field(..., description="状态码")
    message: str = Field(..., description="消息")
    data: Optional[T] = Field(None, description="数据")
    timestamp: int = Field(..., description="时间戳")

    class Config:
        json_encoders = {
            # 可以添加自定义的 JSON 编码器
        }


class SuccessResponse(BaseResponse[T]):
    """成功响应"""

    def __init__(
            self,
            data: Optional[T] = None,
            message: str = "success",
            code: int = ResponseCode.SUCCESS.value
    ):
        import time
        super().__init__(
            code=code,
            message=message,
            data=data,
            timestamp=int(time.time() * 1000)
        )


class ErrorResponse(BaseResponse[None]):
    """错误响应"""

    def __init__(
            self,
            message: str = "error",
            code: int = ResponseCode.BAD_REQUEST.value,
            errors: Optional[List[Dict]] = None
    ):
        import time
        super().__init__(
            code=code,
            message=message,
            data=None,
            timestamp=int(time.time() * 1000)
        )
        if errors:
            self.errors = errors


class Pagination(BaseModel):
    """分页信息"""
    total: int = Field(..., description="总记录数")
    page: int = Field(..., description="当前页码")
    size: int = Field(..., description="每页大小")
    pages: int = Field(..., description="总页数")


class PaginatedResponse(BaseResponse[T]):
    """分页响应"""
    pagination: Optional[Pagination] = Field(None, description="分页信息")

    def __init__(
            self,
            data: Optional[T] = None,
            pagination: Optional[Pagination] = None,
            message: str = "success",
            code: int = ResponseCode.SUCCESS.value
    ):
        import time
        super().__init__(
            code=code,
            message=message,
            data=data,
            timestamp=int(time.time() * 1000)
        )
        self.pagination = pagination


# 快捷方法
def response_success(
        data: Any = None,
        message: str = "success",
        code: int = ResponseCode.SUCCESS.value
) -> SuccessResponse:
    """快速创建成功响应"""
    return SuccessResponse(data=data, message=message, code=code)


def response_error(
        message: str = "error",
        code: int = ResponseCode.BAD_REQUEST.value,
        errors: Optional[List[Dict]] = None
) -> ErrorResponse:
    """快速创建错误响应"""
    return ErrorResponse(message=message, code=code, errors=errors)


def paginated(
        data: Any,
        total: int,
        page: int,
        size: int,
        message: str = "success"
) -> PaginatedResponse:
    """快速创建分页响应"""
    pages = (total + size - 1) // size  # 计算总页数
    pagination = Pagination(
        total=total,
        page=page,
        size=size,
        pages=pages
    )
    return PaginatedResponse(
        data=data,
        pagination=pagination,
        message=message
    )
