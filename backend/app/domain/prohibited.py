"""Стоп-слова для модерации объявлений (UC-6: услуги, еда, медикаменты запрещены)."""
PROHIBITED_KEYWORDS: tuple[str, ...] = (
    "услуга", "ремонт под ключ", "вызов мастера", "готовлю", "еда", "еда на заказ",
    "лекарств", "медикамент", "таблетк", "алкоголь", "сигарет", "оруж", "нож охотнич",
)


def contains_prohibited(text: str | None) -> bool:
    if not text:
        return False
    lowered = text.lower()
    return any(word in lowered for word in PROHIBITED_KEYWORDS)
