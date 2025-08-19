#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ===== НАСТРОЙКИ (отредактируйте под себя) ===============================
INPUT_PATH  = r"temp/export1.txt"  # что парсить
OUTPUT_PATH = r"temp/export_pretty.json"  # куда писать (можно как INPUT_PATH, чтобы перезаписать)
INDENT = 4                                  # размер отступа
SORT_KEYS = False                           # сортировать ключи словарей по алфавиту?
# ==========================================================================

import json
import sys
from pathlib import Path
from json.decoder import JSONDecodeError

def _show_json_error(e: JSONDecodeError, text: str) -> str:
    line = e.lineno or 1
    col = e.colno or 1
    lines = text.splitlines()
    bad_line = lines[line - 1] if 0 <= line - 1 < len(lines) else ""
    pointer = " " * (max(col - 1, 0)) + "^"
    return (
        f"Ошибка JSON: {e.msg}\n"
        f"Строка {line}, столбец {col}\n"
        f"{bad_line}\n{pointer}"
    )

def _read_text(path_str: str) -> str:
    p = Path(path_str).expanduser()
    if not p.exists():
        print(f"Файл не найден: {p}", file=sys.stderr)
        sys.exit(2)
    return p.read_text(encoding="utf-8-sig")

def _try_parse_standard(text: str):
    return json.loads(text)

def _try_parse_json5(text: str):
    try:
        import json5  # pip install json5
    except Exception:
        return None, "json5 недоступен"
    try:
        return json5.loads(text), None
    except Exception as e:
        return None, str(e)

def _try_parse_ndjson(text: str):
    """Каждая непустая строка — отдельный JSON-объект. Возвращаем список объектов."""
    lines = [ln for ln in text.splitlines() if ln.strip()]
    items = []
    for i, ln in enumerate(lines, 1):
        try:
            items.append(json.loads(ln))
        except JSONDecodeError:
            # Попробуем через json5, если есть
            try:
                import json5  # type: ignore
                items.append(json5.loads(ln))  # type: ignore
            except Exception as e:
                # укажем конкретную строку NDJSON
                raise JSONDecodeError(f"NDJSON: ошибка в строке {i}: {e}", ln, 0)
    return items

def read_data_smart(path_str: str):
    text = _read_text(path_str)

    # 1) Обычный JSON
    try:
        return _try_parse_standard(text), "json"
    except JSONDecodeError as e1:
        std_err = _show_json_error(e1, text)

    # 2) JSON5 (комментарии, хвостовые запятые, одинарные кавычки и т.п.)
    data5, err5 = _try_parse_json5(text)
    if data5 is not None:
        return data5, "json5"

    # 3) NDJSON (по объекту в строке)
    try:
        return _try_parse_ndjson(text), "ndjson"
    except JSONDecodeError as e3:
        ndjson_err = str(e3)

    # Если не смогли распарсить — покажем лучшую подсказку
    print("Не удалось распарсить файл как JSON/JSON5/NDJSON.", file=sys.stderr)
    print("\n--- Стандартный JSON сказал:\n" + std_err, file=sys.stderr)
    if err5 != "json5 недоступен":
        print("\n--- JSON5 сказал:\n" + (err5 or ""), file=sys.stderr)
    else:
        print("\n--- Подсказка: установите поддержку JSON5:\n"
              "pip install json5", file=sys.stderr)
    print("\n--- NDJSON сказал:\n" + ndjson_err, file=sys.stderr)
    sys.exit(3)

def write_json_file(data: object, path_str: str, indent: int, sort_keys: bool) -> None:
    p = Path(path_str).expanduser()
    p.parent.mkdir(parents=True, exist_ok=True)
    pretty = json.dumps(data, ensure_ascii=False, indent=max(int(indent), 0), sort_keys=bool(sort_keys))
    p.write_text(pretty + "\n", encoding="utf-8")

def main() -> None:
    if not INPUT_PATH or not OUTPUT_PATH:
        print("Задайте INPUT_PATH и OUTPUT_PATH в начале файла.", file=sys.stderr)
        sys.exit(1)

    data, mode = read_data_smart(INPUT_PATH)
    write_json_file(data, OUTPUT_PATH, INDENT, SORT_KEYS)
    print(f"Готово ({mode}): {OUTPUT_PATH}")

if __name__ == "__main__":
    main()