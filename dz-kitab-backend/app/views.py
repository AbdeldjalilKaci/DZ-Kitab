from rest_framework.generics import ListAPIView
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from .models import Announcement
from .serializers import AnnouncementSerializer
from .filters import AnnouncementAdvancedFilter
from .pagination import AnnouncementSearchPagination

class AnnouncementAdvancedSearchView(ListAPIView):

    queryset = Announcement.objects.select_related('book').filter(status='Active')
    serializer_class = AnnouncementSerializer
    pagination_class = AnnouncementSearchPagination

    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = AnnouncementAdvancedFilter

    ordering_fields = ['price', 'created_at', 'book__published_date']
    ordering = ['-created_at']
