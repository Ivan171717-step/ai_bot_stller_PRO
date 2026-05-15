import json
from pathlib import Path

EXAMPLES_DIR = Path("examples")


def load_examples() -> list[dict]:
    EXAMPLES_DIR.mkdir(exist_ok=True)
    items: list[dict] = []
    for fp in sorted(EXAMPLES_DIR.glob("*.json")):
        try:
            data = json.loads(fp.read_text(encoding="utf-8"))
            data["_slug"] = fp.stem
            items.append(data)
        except Exception:
            continue
    return items


def find_example(query: str) -> dict | None:
    q = query.lower().strip()
    for ex in load_examples():
        hay = " ".join([
            ex.get("title", ""),
            ex.get("business_type", ""),
            " ".join(ex.get("features", [])),
        ]).lower()
        if q in hay:
            return ex
    return None


def format_example(ex: dict, index: int | None = None) -> str:
    prefix = f"{index}. " if index else ""
    text = (
        f"{prefix}<b>{ex.get('title', 'Пример')}</b>\n"
        f"{ex.get('short_description', '')}\n\n"
        f"<b>Бизнес:</b> {ex.get('business_type', 'Не указано')}\n"
        f"<b>Функции:</b>\n— " + "\n— ".join(ex.get("features", [])) + "\n\n"
        f"<b>Преимущества:</b>\n— " + "\n— ".join(ex.get("benefits", [])) + "\n\n"
        f"{ex.get('sales_text', '')}"
    )
    demo_link = (ex.get("demo_link") or "").strip()
    if demo_link:
        text += f"\n\nДемо: {demo_link}"
    return text
