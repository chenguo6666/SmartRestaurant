from rest_framework.response import Response
from rest_framework import status


class APIResponse:
    """统一API响应类"""
    
    @staticmethod
    def success(data=None, message="操作成功", code=200, status_code=status.HTTP_200_OK):
        return Response({
            'code': code,
            'message': message,
            'data': data,
            'errors': None
        }, status=status_code)
    
    @staticmethod
    def error(message="操作失败", errors=None, code=400, status_code=status.HTTP_400_BAD_REQUEST):
        return Response({
            'code': code,
            'message': message,
            'data': None,
            'errors': errors
        }, status=status_code)
    
    @staticmethod
    def created(data=None, message="创建成功"):
        return APIResponse.success(data, message, 201, status.HTTP_201_CREATED)
    
    @staticmethod
    def no_content(message="删除成功"):
        return APIResponse.success(None, message, 204, status.HTTP_204_NO_CONTENT)
    
    @staticmethod
    def unauthorized(message="未授权访问"):
        return APIResponse.error(message, None, 401, status.HTTP_401_UNAUTHORIZED)
    
    @staticmethod
    def forbidden(message="权限不足"):
        return APIResponse.error(message, None, 403, status.HTTP_403_FORBIDDEN)
    
    @staticmethod
    def not_found(message="资源不存在"):
        return APIResponse.error(message, None, 404, status.HTTP_404_NOT_FOUND) 