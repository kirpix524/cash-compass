from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter
def repeat(value: str, times: int) -> str:
    """
    Повторяет строку value указанное количество раз.
    """
    return mark_safe(value * int(times))