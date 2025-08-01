from django.contrib import admin
from .models import Currency, Category


@admin.register(Currency)
class CurrencyAdmin(admin.ModelAdmin):
    list_display: list[str] = ['short', 'name', 'state', 'version', 'acc']
    search_fields: list[str] = ['short', 'name', 'guid']
    list_filter: list[str] = ['state']
    readonly_fields: list[str] = ['guid', 'item_type']
    ordering: list[str] = ['name']

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display: list[str] = ['name', 'category_type', 'state', '_version', '_acc', 'parent']
    search_fields: list[str] = ['name', 'guid']
    list_filter: list[str] = ['state', 'category_type']
    readonly_fields: list[str] = ['guid', 'item_type']
    ordering: list[str] = ['name']