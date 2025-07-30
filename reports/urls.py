from django.urls import path
from django.views.generic import TemplateView

app_name = 'reports'

urlpatterns = [
    path('', TemplateView.as_view(template_name='reports/list.html'), name='list'),
]