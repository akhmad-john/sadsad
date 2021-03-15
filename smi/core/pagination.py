from collections import OrderedDict

from rest_framework import pagination, mixins
from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from rest_framework.utils.urls import replace_query_param, remove_query_param
from threadlocals.threadlocals import get_current_request


class PageNumberPagination(pagination.PageNumberPagination):
    page_size_query_param = 'page_size'

    def paginate_queryset(self, queryset, request, view=None):
        """
        Paginate a queryset if required, either returning a
        page object, or `None` if pagination is not configured for this view.
        """
        self.page = None
        try:
            return super().paginate_queryset(queryset=queryset, request=request, view=view)
        except NotFound as exc:
            return list()

    def get_paginated_response(self, data):
        return Response(OrderedDict([
            ('count', self.page.paginator.count if self.page and self.page.paginator else 0),
            ('next_page', self.get_next_page_number()),
            ('page_size', self.get_page_size(getattr(self, 'request', get_current_request()))),
            ('current_page', self.get_current_page_number()),
            ('previous_page', self.get_previous_page_number()),
            ('next', self.get_next_link()),
            ('previous', self.get_previous_link()),
            ('results', data)
        ]))

    def get_next_link(self):
        if not self.page or not self.page.has_next():
            return None
        url = self.request.build_absolute_uri()
        page_number = self.page.next_page_number()
        return replace_query_param(url, self.page_query_param, page_number)

    def get_previous_link(self):
        if not self.page or not self.page.has_previous():
            return None
        url = self.request.build_absolute_uri()
        page_number = self.page.previous_page_number()
        if page_number == 1:
            return remove_query_param(url, self.page_query_param)
        return replace_query_param(url, self.page_query_param, page_number)

    def get_next_page_number(self):
        return self.page.next_page_number() if self.page and self.page.has_next() else None

    def get_previous_page_number(self):
        return self.page.previous_page_number() if self.page and self.page.has_previous() else None

    def get_current_page_number(self):
        return self.page.number if self.page else 1
