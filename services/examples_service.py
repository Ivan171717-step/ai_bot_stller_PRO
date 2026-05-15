import json
from pathlib import Path

EXAMPLES_DIR = Path("examples")


def load_examples() -> list[dict]:
    EXAMPLES_DIR.mkdir(exist_ok=True)
    items = []
    for fp in sorted(EXAMPLES_DIR.glob("*.json")):
        try:
            data = json.loads(fp.read_text(encoding="utf-8"))
            data["_slug"] = fp.stem
            items.append(data)
        except Exception:
            continue
    return items


def search_examples(query: str, limit: int = 3) -> list[dict]:
    q = (query or "").lower().strip()
    tokens = [t for t in q.split() if t]
    ranked = []
    for ex in load_examples():
        hay_parts = [ex.get("title", ""), ex.get("short_description", ""), ex.get("business_type", ""), " ".join(ex.get("features", [])), " ".join(ex.get("benefits", [])), ex.get("sales_text", "")]
        hay = " ".join(hay_parts).lower()
        score = 0
        if q and q in hay:
            score += 10
        for t in tokens:
            if t in hay:
                score += 2
        if q in ["сложные", "hard"] and ex.get("internal_complexity") == "hard":
            score += 12
        if "ai" in q and "ai" in hay:
            score += 8
        if "webapp" in q and "webapp" in hay:
            score += 8
        if score > 0:
            ranked.append((score, ex))
    ranked.sort(key=lambda x: x[0], reverse=True)
    return [x[1] for x in ranked[:limit]]


def format_example(ex: dict, index: int | None = None) -> str:
    prefix = f"{index}. " if index else ""
    return (
        f"{prefix}<b>{ex.get('title', 'Пример')}</b>\n"
        f"{ex.get('short_description', '')}\n\n"
        f"<b>Бизнес:</b> {ex.get('business_type', 'Не указано')}\n"
        f"<b>Функции:</b>\n— " + "\n— ".join(ex.get("features", [])) + "\n\n"
        f"<b>Преимущества:</b>\n— " + "\n— ".join(ex.get("benefits", [])) + "\n\n"
        f"{ex.get('sales_text', '')}"
    )
