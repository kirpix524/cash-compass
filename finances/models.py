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
    TRANSACTION_TYPE_CHOICES = [
        ("EXPENSE", "EXPENSE"),
        ("INCOME", "INCOME"),
        ("TRANSFER", "TRANSFER"),
    ]
    TRANSACTION_STATE_CHOICES = [
        ("ACTIVE", "ACTIVE"),
        ("DELETED", "DELETED"),
    ]
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name='transactions')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    # … остальные поля …


    # из entries.*
    guid          = models.CharField(max_length=64, unique=True, db_index=True)  # entries.guid
    user          = models.ForeignKey(settings.AUTH_USER_MODEL,
                                      on_delete=models.CASCADE,
                                      related_name="transactions")
    account_guid  = models.CharField(max_length=64)                               # entries.acc
    occurred_at   = models.DateTimeField()                                        # entries.date
    t_type        = models.CharField(max_length=8, choices=TRANSACTION_TYPE_CHOICES)  # entries.type
    state         = models.CharField(max_length=7, choices=TRANSACTION_STATE_CHOICES, default="ACTIVE")
    version       = models.IntegerField(default=0)                                 # entries.ver
    description   = models.CharField(max_length=500, blank=True)                   # entries.desc
    images        = models.JSONField(blank=True, null=True)                        # entries.imgs (список)
    item_type     = models.CharField(max_length=32, default="TRANSACTION")         # itemType

    # опциональные поля из некоторых записей
    template_guid = models.CharField(max_length=64, blank=True, null=True)         # entries.template
    template_key  = models.CharField(max_length=64, blank=True, null=True)         # entries.templateKey

    # ВСЕ подстроки транзакции как есть (список словарей из entries.sub[]).
    # Внутри будут поля: guid, type, from, to, val1, val2, cur1, cur2, state, ver …
    # В from/to могут быть GUID кошелька или категории — мы их не резолвим здесь.
    sub           = models.JSONField()                                             # entries.sub

    # Удобные денормализованные суммы по активным подстрокам
    total_src     = models.DecimalField(max_digits=20, decimal_places=2, default=0)  # Σ val1 ACTIVE
    total_dst     = models.DecimalField(max_digits=20, decimal_places=2, default=0)  # Σ val2 ACTIVE

    class Meta:
        ordering = ["-occurred_at", "-id"]
        indexes = [
            Index(fields=["user", "occurred_at"]),
            Index(fields=["t_type"]),
            Index(fields=["state"]),
        ]

    def __str__(self):
        return f"{self.t_type} @ {self.occurred_at:%Y-%m-%d %H:%M}"

    # ── удобства ─────────────────────────────────────────────────────────────────

    def recalc_totals(self):
        """Пересчитать total_src/total_dst по ACTIVE-подстрокам."""
        t1 = Decimal("0")
        t2 = Decimal("0")
        for line in (self.sub or []):
            if line.get("state") == "DELETED":
                continue
            v1 = line.get("val1")
            v2 = line.get("val2")
            if v1 not in (None, ""):
                t1 += Decimal(str(v1))
            if v2 not in (None, ""):
                t2 += Decimal(str(v2))
        self.total_src = t1
        self.total_dst = t2

    def save(self, *args, **kwargs):
        # если sub менялся (или сохраняем впервые) — пересчитаем суммы
        update_fields = kwargs.get("update_fields")
        if update_fields is None or "sub" in update_fields:
            self.recalc_totals()
            if update_fields is not None:
                kwargs["update_fields"] = list(set(update_fields) | {"total_src", "total_dst"})
        super().save(*args, **kwargs)

    @property
    def from_guids(self) -> set[str]:
        """Множество всех from GUID по активным строкам."""
        return {l["from"] for l in (self.sub or []) if l.get("state") != "DELETED" and "from" in l}

    @property
    def to_guids(self) -> set[str]:
        """Множество всех to GUID по активным строкам."""
        return {l["to"] for l in (self.sub or []) if l.get("state") != "DELETED" and "to" in l}