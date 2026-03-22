# kitajalan/templatetags/custom_filters.py
from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """
    Template filter untuk mengakses dictionary dengan key
    Penggunaan: {{ my_dict|get_item:key }}
    """
    if dictionary is None:
        return None
    return dictionary.get(key)

@register.filter
def is_in_list(value, the_list):
    """
    Cek apakah value ada dalam list
    Penggunaan: {{ value|is_in_list:list }}
    """
    return value in the_list

@register.filter
def subtract(value, arg):
    """
    Pengurangan
    Penggunaan: {{ value|subtract:arg }}
    """
    try:
        return int(value) - int(arg)
    except (ValueError, TypeError):
        return value

@register.filter
def multiply(value, arg):
    """
    Perkalian
    Penggunaan: {{ value|multiply:arg }}
    """
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return value

@register.filter
def percentage(value, total):
    """
    Menghitung persentase
    Penggunaan: {{ value|percentage:total }}
    """
    try:
        if total and total > 0:
            return int((float(value) / float(total)) * 100)
        return 0
    except (ValueError, TypeError, ZeroDivisionError):
        return 0
    