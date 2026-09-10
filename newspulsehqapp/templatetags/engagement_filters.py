from django import template

from newspulsehqapp.utils import format_count

register = template.Library()


@register.filter(name="format_count")
def format_count_filter(value):
    return format_count(value)
