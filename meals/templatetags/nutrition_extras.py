from django import template

register = template.Library()

@register.filter
def nutrient_percent(nutrient_value, recommended_value):
    """
    Returns what percent 'nutrient_value' is of 'recommended_value'.
    Example: if recommended_value=200 and nutrient_value=50, returns 25.
    """
    try:
        if recommended_value:
            return (nutrient_value / recommended_value) * 100
        return 0
    except (TypeError, ZeroDivisionError):
        return 0
