import json
from typing import IO

from users.models import User
from .models import Currency, Category


class CurrencyImporter:
    """
    Сервис для импорта валют из JSON-файла.
    """
    def __init__(self, file: IO, user: User) -> None:
        self._file = file
        self._user = user
        self._created_count = 0

    def import_currencies(self) -> int:
        data = json.load(self._file)
        for item in data.get("CURRENCY", []):
            e = item["entries"]
            # если у пользователя нет acc, заполняем из файла
            if not self._user.acc:
                self._user.acc = e.get("acc")
                self._user.save()
            guid = e.get("guid")
            if not guid:
                continue
            obj, created = Currency.objects.update_or_create(
                guid=guid,
                user=self._user,
                defaults={
                    "version": e.get("ver"),
                    "name": e.get("name"),
                    "short": e.get("short"),
                    "state": e.get("state"),
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

    def __init__(self, file: IO, user: User) -> None:
        self._file = file
        self._user = user
        self._created_count = 0

    def import_categories(self) -> int:
        data = json.load(self._file)
        # вместо простой мапы entries теперь запомним и itemType
        entries_map = {
            item["entries"]["guid"]: {
                "entries": item["entries"],
                "item_type": item.get("itemType", "CATEGORY")
            }
            for item in data.get("CATEGORY", [])
            if "guid" in item.get("entries", {})
        }
        # если нужно заполнять user.acc, делаем это здесь...
        processed = set()

        def save_node(guid):
            if guid in processed:
                return
            rec = entries_map.get(guid)
            if not rec:
                return
            e = rec["entries"]
            # сначала сохраним родителя
            parent = None
            parent_guid = e.get("parent")
            if parent_guid:
                save_node(parent_guid)
                parent = Category.objects.get(guid=parent_guid, user=self._user)
            # а теперь создаём/обновляем саму категорию
            obj, created = Category.objects.update_or_create(
                guid=guid,
                user=self._user,
                defaults={
                    "name": e.get("name"),
                    "state": e.get("state"),
                    "category_type": e.get("type"),
                    "_version": e.get("ver"),
                    "parent": parent,
                    "item_type": rec["item_type"],   # берём из rec, а не из несуществующей item
                }
            )
            if created:
                self._created_count += 1
            processed.add(guid)

        for guid in entries_map:
            save_node(guid)

        return self._created_count