import uuid
from collections import defaultdict
from types import SimpleNamespace
from typing import Any, Dict
from django.views.generic import ListView
from django.views.generic.edit import FormMixin, UpdateView, CreateView, FormView
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Prefetch, Sum
from django.shortcuts import redirect
from django.urls import reverse_lazy


from .models import Currency, Category, WalletGroup, Wallet
from .forms import CurrencyUploadForm, CategoryUploadForm, WalletUploadForm
from .services import CurrencyImporter, CategoryImporter, WalletImporter


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
            importer = CurrencyImporter(uploaded_file, request.user)
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
            importer = CategoryImporter(form.cleaned_data['file'], request.user)
            count = importer.import_categories()
            messages.success(request, f'Загружено {count} новых категорий.')
        else:
            messages.error(request, 'Ошибка загрузки файла.')
        return redirect(self.success_url)


class CategoryUpdateView(LoginRequiredMixin, UpdateView):
    model = Category
    fields: list[str] = ['name', 'parent']
    template_name: str = "finances/category_modal_form.html"
    success_url = reverse_lazy('finances:categories')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, "Категория успешно обновлена")
        return response

class CategoryCreateView(LoginRequiredMixin, CreateView):
    model = Category
    fields: list[str] = ['name', 'parent']
    template_name: str = "finances/category_modal_form.html"
    success_url = reverse_lazy('finances:categories')

    def form_valid(self, form):
        form.instance.user = self.request.user
        if not form.instance.guid:
            form.instance.guid = uuid.uuid4().hex
        form.instance.category_type = self.request.POST.get('category_type')
        return super().form_valid(form)

class WalletListView(LoginRequiredMixin, FormMixin, ListView):
    template_name = 'finances/wallets.html'
    context_object_name = 'wallet_groups'
    form_class = WalletUploadForm
    success_url = reverse_lazy('finances:wallets')

    def get_queryset(self):
        user = self.request.user

        # 1) Берём все «реальные» группы
        groups = list(
            WalletGroup.objects
                .filter(state='ACTIVE', user=user)
                .annotate(total_balance=Sum('wallets__current_balance'))
                .prefetch_related('wallets')
        )

        # 2) Кошельки без группы
        ungrouped_qs = Wallet.objects.filter(
            group__isnull=True,
            state='ACTIVE',
            user=user
        )

        if ungrouped_qs.exists():
            total = ungrouped_qs.aggregate(sum=Sum('current_balance'))['sum'] or 0
            dummy = SimpleNamespace(
                name='Без группы',
                total_balance=total,
                wallets=list(ungrouped_qs),
                is_virtual=True,
            )
            groups.insert(0, dummy)

        return groups

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            importer = WalletImporter(form.cleaned_data['file'], request.user)
            count = importer.import_wallets()
            messages.success(request, f'Загружено {count} новых записей (группы + кошельки).')
        else:
            messages.error(request, 'Ошибка загрузки файла.')
        return redirect(self.success_url)