from django import template

register = template.Library()



@register.filter(name='abs')
def abs_filter(value):
    try:
        if value is None:
            return 0
        return abs(float(value))
    except (TypeError, ValueError):
        return value
