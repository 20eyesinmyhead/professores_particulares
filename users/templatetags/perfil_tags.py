# professores_particulares/users/templatetags/perfil_tags.py

from django import template

# Esta linha é o ponto de entrada. Deve ter exatamente este nome.
register = template.Library()

@register.filter
def has_attr(obj, attr_name):
    """
    Verifica se um objeto possui um determinado atributo (campo).
    """
    return hasattr(obj, attr_name)

# Certifique-se de que não há NENHUM outro código ou print() neste arquivo.