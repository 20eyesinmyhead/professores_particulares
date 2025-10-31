from django import template

register = template.Library()

@register.filter(name='split')
def split_string(value, key):
    """
    Retorna a string dividida pelo separador.
    Uso: {{ algum_texto|split:"," }} 
    """
    if value:
        return value.split(key)
    return []