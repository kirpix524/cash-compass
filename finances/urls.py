from django.urls import path
from django.views.generic import TemplateView
from .views import CurrencyListView, CategoryListView

app_name = 'finances'

urlpatterns = [
    path('wallets/', TemplateView.as_view(template_name='finances/wallets.html'), name='wallets'),
    path('transactions/', TemplateView.as_view(template_name='finances/transactions.html'), name='transactions'),
    path('currencies/', CurrencyListView.as_view(), name='currencies'),
    path('categories/', CategoryListView.as_view(), name='categories'),
]