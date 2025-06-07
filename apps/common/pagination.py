from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class StandardResultsSetPagination(PageNumberPagination):
    """标准分页类"""
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100
    page_query_param = 'page'
    
    def get_paginated_response(self, data):
        return Response({
            'code': 200,
            'message': '获取成功',
            'data': {
                'results': data,
                'pagination': {
                    'count': self.page.paginator.count,
                    'current_page': self.page.number,
                    'total_pages': self.page.paginator.num_pages,
                    'page_size': self.get_page_size(self.request),
                    'has_next': self.page.has_next(),
                    'has_previous': self.page.has_previous(),
                }
            },
            'errors': None
        })


class LargeResultsSetPagination(PageNumberPagination):
    """大数据集分页"""
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 200
    
    def get_paginated_response(self, data):
        return Response({
            'code': 200,
            'message': '获取成功',
            'data': {
                'results': data,
                'pagination': {
                    'count': self.page.paginator.count,
                    'current_page': self.page.number,
                    'total_pages': self.page.paginator.num_pages,
                    'page_size': self.get_page_size(self.request),
                    'has_next': self.page.has_next(),
                    'has_previous': self.page.has_previous(),
                }
            },
            'errors': None
        }) 