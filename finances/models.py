import uuid
from typing import Optional
from django.db import models

class Currency(models.Model):
    """
    Модель валюты для CashCompass.
    """
    guid: str = models.CharField(
        primary_key=True,
        max_length=100,
        editable=False,
        verbose_name="GUID валюты"
    )
    acc: uuid.UUID = models.UUIDField(
        verbose_name="GUID аккаунта",
        help_text="Идентификатор счёта, к которому привязана валюта"
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
        choices=[
            ("ACTIVE", "Активна"),
            ("INACTIVE", "Неактивна"),
        ],
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
        max_length=100,
        primary_key=True,
        editable=False,
        verbose_name="GUID категории"
    )
    _acc: uuid.UUID = models.UUIDField(
        verbose_name="GUID счёта",
        help_text="Идентификатор аккаунта из источника"
    )
    _version: int = models.PositiveIntegerField(
        verbose_name="Версия записи",
        help_text="ver из JSON"
    )
    name: str = models.CharField(
        max_length=255,
        verbose_name="Название категории"
    )
    state: str = models.CharField(
        max_length=20,
        choices=[
            ("ACTIVE", "Активна"),
            ("DELETED", "Удалена"),
        ],
        default="ACTIVE",
        verbose_name="Состояние категории"
    )
    category_type: str = models.CharField(
        max_length=10,
        choices=[
            ("EXPENSE", "Расход"),
            ("INCOME", "Доход"),
        ],
        verbose_name="Тип категории"
    )
    parent: Optional["Category"] = models.ForeignKey(
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