from collections import defaultdict
from typing import Any, Dict
from django.views.generic import ListView
from django.views.generic.edit import FormMixin
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Prefetch
from django.shortcuts import redirect
from django.urls import reverse_lazy


from .models import Currency, Category
from .forms import CurrencyUploadForm, CategoryUploadForm
from .services import CurrencyImporter, CategoryImporter


class CurrencyListView(LoginRequiredMixin, FormMixin, ListView):
    model = Currency
    template_name: str = "finances/currencies.html"
    form_class = CurrencyUploadForm
    success_url = reverse_lazy('finances:currencies')

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context: Dict[str, Any] = super().get_context_data(**kwargs)
        if 'form' not in context:
            context['form'] = self.get_form()
        return context

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            uploaded_file = form.cleaned_data['file']
            importer = CurrencyImporter(uploaded_file)
            created = importer.import_currencies()
            messages.success(request, f'Загружено {created} новых валют.')
        else:
            messages.error(request, 'Ошибка загрузки файла.')
        return redirect(self.success_url)

class CategoryListView(LoginRequiredMixin, FormMixin, ListView):
    model = Category
    template_name = "finances/categories.html"
    context_object_name = "all_categories"
    form_class = CategoryUploadForm
    success_url = reverse_lazy('finances:categories')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        # 1. Берём все активные категории сразу
        all_cats = Category.objects.filter(state="ACTIVE").order_by("name")
        # 2. Группируем их по parent_id
        children_map = defaultdict(list)
        for cat in all_cats:
            parent_id = cat.parent_id  # None для корней
            children_map[parent_id].append(cat)
        # 3. Рекурсивно собираем дерево
        def build_tree(nodes):
            tree = []
            for node in nodes:
                node.children_cache: list[Category] = build_tree(children_map.get(node.guid, []))
                tree.append(node)
            return tree

        # корневые расходы и доходы
        roots = children_map[None]
        expense_tree = [n for n in roots if n.category_type=="EXPENSE"]
        income_tree  = [n for n in roots if n.category_type=="INCOME"]

        ctx["expense_categories"] = build_tree(expense_tree)
        ctx["income_categories"]  = build_tree(income_tree)
        return ctx

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            importer = CategoryImporter(form.cleaned_data['file'])
            count = importer.import_categories()
            messages.success(request, f'Загружено {count} новых категорий.')
        else:
            messages.error(request, 'Ошибка загрузки файла.')
        return redirect(self.success_url)