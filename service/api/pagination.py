from rest_framework.pagination import PageNumberPagination


class ServicePagination(PageNumberPagination):
    page_size = 5
    page_size_query_param = 'page_size'  # client can ask ?page_size=10
    max_page_size = 50
