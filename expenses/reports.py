from collections import OrderedDict

from django.db.models import Sum, Value
from django.db.models.functions import Coalesce, TruncMonth, TruncYear

def summary_per_category(queryset):
    return OrderedDict(sorted(
        queryset
        .annotate(category_name=Coalesce('category__name', Value('-')))
        .order_by()
        .values('category_name')
        .annotate(s=Sum('amount'))
        .values_list('category_name', 's')
    ))


def summary_per_year_month(queryset):

    year_month_data = (
        queryset
        .annotate(year=TruncYear('date'), month=TruncMonth('date'))
        .values('year', 'month')
        .annotate(total_amount=Sum('amount'))
        .order_by('year', 'month')
    )


    summary = [
        {
            'year': entry['year'].year,
            'month': entry['month'].month,
            'total_amount': entry['total_amount']
        }
        for entry in year_month_data
    ]

    return summary