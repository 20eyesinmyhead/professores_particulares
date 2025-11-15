"""
Definição de Tags de Template Customizadas para o app 'users'.

Este arquivo contém filtros e tags relacionados à lógica de perfis.

Para usar os filtros deste arquivo em um template, você deve
primeiro carregá-los com: {% load perfil_tags %}
"""

from django import template

# Cria uma instância da biblioteca de templates,
# que é usada para "registrar" novos filtros e tags.
register = template.Library()

@register.filter(name='has_attr')
def has_attr(obj, attr_name):
    """
    Filtro de template customizado que verifica se um objeto (como um
    modelo do Django) possui um determinado atributo (campo ou método).

    Isso permite fazer verificações de segurança dentro do template
    antes de tentar acessar um atributo que pode não existir.
    
    Uso no template:
        {% if meu_objeto|has_attr:"nome_do_campo" %}
            <p>{{ meu_objeto.nome_do_campo }}</p>
        {% endif %}
    
    Parâmetros:
        obj (object): O objeto a ser verificado (ex: 'user_perfil').
        attr_name (str): O nome do atributo que estamos procurando.
    """
    # 'hasattr()' é uma função nativa do Python que retorna
    # True se o 'obj' tiver um atributo com o nome 'attr_name',
    # e False caso contrário.
    return hasattr(obj, attr_name)

# Nota: O nome do arquivo (ex: 'perfil_tags.py') é o nome que você
# usa para carregar as tags no template: {% load perfil_tags %}