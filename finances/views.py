from typing import Any, Dict
import json
from django.views.generic import ListView
from django.views.generic.edit import FormMixin
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.shortcuts import redirect
from django.contrib import messages
from .models import Currency
from .forms import CurrencyUploadForm
from .services import CurrencyImporter


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