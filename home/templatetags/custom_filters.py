# custom_filters.py
from django import template

register = template.Library()

@register.filter
def custom_range(value):
    return range(value)
