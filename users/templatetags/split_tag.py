"""
Definição de Tags de Template Customizadas para o app 'users'.

Este arquivo contém filtros utilitários de manipulação de texto.

Para usar os filtros deste arquivo em um template, você deve
primeiro carregá-los com: {% load split_tag %}
"""

from django import template

# Cria uma instância da biblioteca de templates,
# que é usada para "registrar" novos filtros e tags.
register = template.Library()

@register.filter(name='split')
def split_string(value, key):
    """
    Filtro de template customizado que divide (split) uma string
    em uma lista, usando um 'key' (separador) fornecido.

    Isso é muito útil para campos de texto que armazenam múltiplos
    valores separados por vírgula (ex: o campo 'disciplinas').
    
    Uso no template:
    
        {% for item in professor.disciplinas|split:"," %}
            <span class="badge">{{ item }}</span>
        {% endfor %}
    
    Parâmetros:
        value (str): A string a ser dividida (ex: "Matemática,Física").
        key (str): O caractere separador (ex: ",").
    """
    
    # Verifica se o 'value' (a string) não está vazio ou nulo
    if value:
        # 'value.split(key)' é uma função nativa do Python
        # que retorna uma lista de strings.
        # Ex: "Matemática,Física".split(",") -> ['Matemática', 'Física']
        return value.split(key)
    
    # Se o 'value' estiver vazio, retorna uma lista vazia
    # para evitar que o template quebre ao tentar iterar (loop) sobre 'None'.
    return []