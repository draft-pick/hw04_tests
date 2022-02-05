from django.conf import settings
from django.core.paginator import Paginator


def paginator_posts(request, queryset):
    paginator = Paginator(queryset, settings.PAGINATOR_POST_COUNT)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)
