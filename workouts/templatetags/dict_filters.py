from django import template
register = template.Library()

@register.filter
def get_entry_for_subplan(entries_dict, subplan):
    return entries_dict.get(subplan.id)

@register.filter
def format_date(value):
    try:
        dt = datetime.strptime(value, "%Y-%m-%d")
        return dt.strftime("%b %d, %Y")  # e.g., "Apr 10, 2025"
    except Exception:
        return value  # fallback if it can't be parsed

@register.filter
def sort_dates(date_list):
    return sorted(date_list)
