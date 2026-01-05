import django_filters
from django.db.models import Q
from .models import Announcement

class AnnouncementAdvancedFilter(django_filters.FilterSet):

    q = django_filters.CharFilter(method='global_search')

    categories = django_filters.CharFilter(method='filter_categories')
    conditions = django_filters.CharFilter(method='filter_conditions')

    price_min = django_filters.NumberFilter(field_name='price', lookup_expr='gte')
    price_max = django_filters.NumberFilter(field_name='price', lookup_expr='lte')

    pages_min = django_filters.NumberFilter(field_name='book__page_count', lookup_expr='gte')
    pages_max = django_filters.NumberFilter(field_name='book__page_count', lookup_expr='lte')

    published_after = django_filters.CharFilter(field_name='book__published_date', lookup_expr='gte')
    published_before = django_filters.CharFilter(field_name='book__published_date', lookup_expr='lte')

    def global_search(self, queryset, name, value):
        return queryset.filter(
            Q(book__title__icontains=value) |
            Q(book__authors__icontains=value) |
            Q(book__publisher__icontains=value) |
            Q(description__icontains=value) |
            Q(location__icontains=value)
        )

    def filter_categories(self, queryset, name, value):
        return queryset.filter(category__in=value.split(','))

    def filter_conditions(self, queryset, name, value):
        return queryset.filter(condition__in=value.split(','))

    class Meta:
        model = Announcement
        fields = []
