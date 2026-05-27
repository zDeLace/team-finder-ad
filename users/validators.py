import re
from django.core.exceptions import ValidationError


def validate_phone(value: str) -> str:
    """
    Принимает номера вида 8XXXXXXXXXX или +7XXXXXXXXXX.
    Приводит к формату +7XXXXXXXXXX.
    """
    cleaned = re.sub(r"[\s\-\(\)]", "", value)
    pattern_8 = re.compile(r"^8(\d{10})$")
    pattern_plus7 = re.compile(r"^\+7(\d{10})$")

    m = pattern_8.match(cleaned) or pattern_plus7.match(cleaned)
    if not m:
        raise ValidationError(
            "Введите номер в формате 8XXXXXXXXXX или +7XXXXXXXXXX"
        )
    return f"+7{m.group(1)}"


def validate_github_url(value: str) -> None:
    pattern = re.compile(r"^https?://(www\.)?github\.com/.*$", re.IGNORECASE)
    if value and not pattern.match(value):
        raise ValidationError(
            "Допустимы только ссылки на GitHub (https://github.com/...)"
        )
