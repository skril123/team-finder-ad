import json

from django.core.paginator import Paginator

from core.constants import PAGINATE_BY


def paginate_queryset(request, queryset, per_page=PAGINATE_BY):
    paginator = Paginator(queryset, per_page)
    return paginator.get_page(request.GET.get("page"))


def get_request_payload(request):
    if request.content_type == "application/json" and request.body:
        try:
            return json.loads(request.body.decode("utf-8"))
        except json.JSONDecodeError:
            return {}
    return request.POST
