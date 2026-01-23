from rest_framework.generics import ListAPIView
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from app.models import Announcement
from app.serializers import AnnouncementSerializer
from app.filters import AnnouncementAdvancedFilter
from app.pagination import AnnouncementSearchPagination
from app.pagination.announcement_pagination import AnnouncementSearchPagination

class AnnouncementAdvancedSearchView(ListAPIView):

    queryset = Announcement.objects.select_related('book').filter(status='Active')
    serializer_class = AnnouncementSerializer
    pagination_class = AnnouncementSearchPagination

    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = AnnouncementAdvancedFilter

    ordering_fields = ['price', 'created_at', 'book__published_date']
    ordering = ['-created_at']
    from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Q
from app.models import Announcement


class AnnouncementBasicSearchView(APIView):

    def get(self, request):
        queryset = Announcement.objects.filter(status='Active')

        q = request.query_params.get('q')
        category = request.query_params.get('category')
        min_price = request.query_params.get('min_price')
        max_price = request.query_params.get('max_price')

        if q:
            queryset = queryset.filter(
                Q(title__icontains=q) |
                Q(author__icontains=q)
            )

        if category:
            queryset = queryset.filter(category=category)

        if min_price:
            queryset = queryset.filter(price__gte=min_price)

        if max_price:
            queryset = queryset.filter(price__lte=max_price)

        return Response(list(queryset.values()))

