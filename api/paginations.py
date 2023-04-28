from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination


class BasePagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100


class MovieAPIListPagination(PageNumberPagination):
    page_size = 5
    page_size_query_param = "page_size"
    max_page_size = 50

    def get_paginated_response(self, data):
        return Response({
            "count": self.page.paginator.count,
            "links": {
                "next": self.get_next_link(),
                "previous": self.get_previous_link(),
            },
            "result": data
        })
