from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', TemplateView.as_view(template_name='core/index.html'), name='home'),
    path('users/', include('users.urls', namespace='users')),
    path('finances/', include('finances.urls', namespace='finances')),
    path('reports/', include('reports.urls', namespace='reports')),
]