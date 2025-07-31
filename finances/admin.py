from django.contrib import admin
from .models import Currency

@admin.register(Currency)
class CurrencyAdmin(admin.ModelAdmin):
    list_display: list[str] = ['short', 'name', 'state', 'version', 'acc']
    search_fields: list[str] = ['short', 'name', 'guid']
    list_filter: list[str] = ['state']
    readonly_fields: list[str] = ['guid', 'item_type']
    ordering: list[str] = ['name']