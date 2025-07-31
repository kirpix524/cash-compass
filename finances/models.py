import uuid
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