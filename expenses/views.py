from django.db.models import Sum
from django.views.generic.list import ListView

from .forms import ExpenseSearchForm
from .models import Expense, Category
from .reports import summary_per_category, summary_per_year_month


class ExpenseListView(ListView):
    model = Expense
    paginate_by = 20

    def get_context_data(self, *, object_list=None, **kwargs):
        queryset = object_list if object_list is not None else self.object_list

        form = ExpenseSearchForm(self.request.GET)
        if form.is_valid():

            name = form.cleaned_data.get('name', '').strip()
            if name:
                queryset = queryset.filter(name__icontains=name)

            category = form.cleaned_data.get('category')
            if category:
                queryset = queryset.filter(category=category)

            date_from = form.cleaned_data.get('date_from')
            if date_from:
                queryset = queryset.filter(date__gte=date_from)

            date_to = form.cleaned_data.get('date_to')
            if date_to:
                queryset = queryset.filter(date__lte=date_to)

            sort_field = self.request.GET.get('sort', 'date')
            sort_direction = self.request.GET.get('direction', 'desc')
            sort_order = '-' if sort_direction == 'desc' else ''

            if sort_field == 'category':
                sort_field = 'category__name'

            queryset = queryset.order_by(f'{sort_order}{sort_field}')

        total_amount_spent = queryset.aggregate(total=Sum('amount'))['total'] or 0.00
        monthly_summary = summary_per_year_month(queryset)
        return super().get_context_data(
            form=form,
            object_list=queryset,
            summary_per_category=summary_per_category(queryset),
            summary_per_year_month=monthly_summary,
            total_amount=total_amount_spent,
            **kwargs)


class CategoryListView(ListView):
    model = Category
    paginate_by = 20
