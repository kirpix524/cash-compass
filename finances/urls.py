from django.urls import path
from django.views.generic import TemplateView
from .views import CurrencyListView, CategoryListView, CategoryUpdateView, CategoryCreateView, WalletListView

app_name = 'finances'

urlpatterns = [
    path('wallets/', WalletListView.as_view(), name='wallets'),
    path('transactions/', TemplateView.as_view(template_name='finances/transactions.html'), name='transactions'),
    path('currencies/', CurrencyListView.as_view(), name='currencies'),
    path('categories/', CategoryListView.as_view(), name='categories'),
    path('categories/<str:pk>/edit/', CategoryUpdateView.as_view(), name='category_edit'),
    path('categories/add/', CategoryCreateView.as_view(), name='category_add'),
]