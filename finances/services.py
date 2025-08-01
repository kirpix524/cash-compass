import json
from typing import IO
from .models import Currency, Category


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

class CategoryImporter:
    """
    Сервис для импорта категорий из JSON-файла.
    """
    def __init__(self, file: IO) -> None:
        self._file = file
        self._created_count = 0

    def import_categories(self) -> int:
        data = json.load(self._file)
        # создаём маппинг guid → запись entries
        entries = {
            item["entries"]["guid"]: item["entries"]
            for item in data.get("CATEGORY", [])
            if "entries" in item
        }
        processed = set()

        def save_node(guid):
            if guid in processed or guid not in entries:
                return
            entry = entries[guid]
            parent = None
            parent_guid = entry.get("parent")
            if parent_guid:
                save_node(parent_guid)
                parent = Category.objects.get(guid=parent_guid)
            _, created = Category.objects.update_or_create(
                guid=guid,
                defaults={
                    "name": entry.get("name"),
                    "state": entry.get("state"),
                    "category_type": entry.get("type"),
                    "parent": parent,
                    "_acc": entry.get("acc"),
                    "_version": entry.get("ver"),
                }
            )
            if created:
                self._created_count += 1
            processed.add(guid)

        for guid in entries:
            save_node(guid)

        return self._created_count