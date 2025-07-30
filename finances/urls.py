from django.urls import path
from django.views.generic import TemplateView

app_name = 'finances'

urlpatterns = [
    path('wallets/', TemplateView.as_view(template_name='finances/wallets.html'), name='wallets'),
    path('transactions/', TemplateView.as_view(template_name='finances/transactions.html'), name='transactions'),
]