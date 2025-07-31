import json
from typing import IO
from .models import Currency

class CurrencyImporter:
    """
    Сервис для импорта валют из JSON-файла.
    """
    def __init__(self, file: IO) -> None:
        self._file = file
        self._created_count: int = 0

    def import_currencies(self) -> int:
        """
        Парсит JSON из self._file, сохраняет/обновляет записи Currency и
        возвращает число созданных объектов.
        """
        data = json.load(self._file)
        for item in data.get("CURRENCY", []):
            entries = item.get("entries", {})
            guid = entries.get("guid")
            if not guid:
                continue
            _, created = Currency.objects.update_or_create(
                guid=guid,
                defaults={
                    "acc": entries.get("acc"),
                    "version": entries.get("ver"),
                    "name": entries.get("name"),
                    "short": entries.get("short"),
                    "state": entries.get("state"),
                    "item_type": item.get("itemType", "CURRENCY"),
                }
            )
            if created:
                self._created_count += 1
        return self._created_count