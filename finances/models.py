import uuid
from decimal import Decimal
from typing import Optional
from django.db import models
from django.conf import settings

class Currency(models.Model):
    """
    Модель валюты для CashCompass.
    """
    guid: str = models.CharField(
        primary_key=True,
        max_length=40,
        editable=False,
        verbose_name="GUID валюты"
    )
    user: settings.AUTH_USER_MODEL = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="currencies",
        verbose_name="Пользователь"
    )
    version: int = models.PositiveIntegerField(
        verbose_name="Версия записи",
        help_text="Версия данных из источника"
    )
    name: str = models.CharField(
        max_length=255,
        verbose_name="Полное название валюты"
    )
    short: str = models.CharField(
        max_length=10,
        verbose_name="Код валюты (ISO)"
    )
    state: str = models.CharField(
        max_length=20,
        choices=[("ACTIVE", "Активна"), ("INACTIVE", "Неактивна")],
        default="ACTIVE",
        verbose_name="Состояние"
    )
    item_type: str = models.CharField(
        max_length=20,
        default="CURRENCY",
        editable=False,
        verbose_name="Тип элемента"
    )

    class Meta:
        verbose_name = "Валюта"
        verbose_name_plural = "Валюты"
        ordering = ["name"]

    def __str__(self) -> str:
        return f"{self.short} — {self.name}"

class Category(models.Model):
    """
    Модель категории доходов/расходов.
    """
    guid: str = models.CharField(
        max_length=40,
        primary_key=True,
        editable=False,
        verbose_name="GUID категории"
    )
    user: settings.AUTH_USER_MODEL = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="categories",
        verbose_name="Пользователь"
    )
    _version: int = models.PositiveIntegerField(
        verbose_name="Версия записи Efics",
        help_text="Версия Efics из JSON",
        default = 0
    )
    name: str = models.CharField(
        max_length=255,
        verbose_name="Название категории"
    )
    state: str = models.CharField(
        max_length=20,
        choices=[("ACTIVE", "Активна"), ("DELETED", "Удалена")],
        default="ACTIVE",
        verbose_name="Состояние категории"
    )
    category_type: str = models.CharField(
        max_length=10,
        choices=[("EXPENSE", "Расход"), ("INCOME", "Доход")],
        verbose_name="Тип категории"
    )
    parent: "Category" = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="children",
        verbose_name="Родительская категория"
    )
    item_type: str = models.CharField(
        max_length=20,
        default="CATEGORY",
        editable=False,
        verbose_name="Тип элемента"
    )

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name

WALLET_STATE_CHOICES = [
    ('ACTIVE', 'Active'),
    ('DELETED', 'Deleted'),
]

WALLET_TYPE_CHOICES = [
    ('WALLET_GROUP', 'Wallet Group'),
    ('WALLET', 'Wallet'),
]

class WalletGroup(models.Model):
    guid = models.CharField(max_length=64, unique=True, editable=False)
    name = models.CharField(max_length=200)
    img = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(
        max_length=10,
        choices=WALLET_STATE_CHOICES,
        default='ACTIVE'
    )
    _version = models.IntegerField(default=0)
    item_type = models.CharField(
        max_length=20,
        choices=WALLET_TYPE_CHOICES,
        default='WALLET_GROUP',
        editable=False
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='wallet_groups'
    )

    class Meta:
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.guid:
            self.guid = uuid.uuid4().hex
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Wallet(models.Model):
    guid = models.CharField(max_length=64, unique=True, editable=False)
    name = models.CharField(max_length=200)
    img = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(
        max_length=10,
        choices=WALLET_STATE_CHOICES,
        default='ACTIVE'
    )
    _version = models.IntegerField(default=0)
    item_type = models.CharField(
        max_length=20,
        choices=WALLET_TYPE_CHOICES,
        default='WALLET',
        editable=False
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='wallets'
    )

    group = models.ForeignKey(
        WalletGroup,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='wallets'
    )
    currency = models.ForeignKey(
        'Currency',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='wallets'
    )
    current_balance = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name="Текущий баланс"
    )

    class Meta:
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.guid:
            self.guid = uuid.uuid4().hex
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class Transaction(models.Model):
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name='transactions')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    # … остальные поля …