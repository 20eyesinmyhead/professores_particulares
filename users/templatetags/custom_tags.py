"""
Definição de Tags de Template Customizadas para o app 'users'.

Este arquivo permite a criação de "filtros" e "tags" Python
que podem ser usados dentro dos templates HTML do Django para
adicionar lógica ou formatação.

Para usar os filtros deste arquivo em um template, você deve
primeiro carregá-los com: {% load custom_tags %}
"""

from django import template

# Cria uma instância da biblioteca de templates,
# que é usada para "registrar" novos filtros e tags.
register = template.Library()

@register.filter(name='add_class')
def add_class(value, css_class):
    """
    Filtro de template customizado que adiciona classes CSS
    a um campo de formulário (widget) do Django.

    Isso é essencial para aplicar classes do Tailwind (como 'border-gray-300'
    ou 'focus:ring-amber-500') nos campos {{ field }} gerados
    automaticamente pelo Django.
    
    Uso no template:
        {{ form.meu_campo|add_class:"classe_css_1 classe_css_2" }}
    
    Parâmetros:
        value (BoundField): O campo do formulário (ex: form.assunto)
        css_class (str): A string de classes a serem adicionadas.
    """
    
    # Etapa 1: Verificação de Segurança
    # Verifica se o 'value' passado é um campo de formulário válido
    # que possui um widget com um atributo 'attrs' (atributos HTML).
    if hasattr(value, 'field') and hasattr(value.field.widget, 'attrs'):
        
        # Etapa 2: Obter Classes Existentes
        # Pega as classes que o widget já possa ter (definidas no forms.py)
        # ou retorna uma string vazia se não houver nenhuma.
        existing_classes = value.field.widget.attrs.get('class', '')
        
        # Etapa 3: Concatenar Novas Classes
        # Adiciona a nova 'css_class' à lista de 'existing_classes'.
        if existing_classes:
            # Garante que haja um espaço entre as classes
            classes = existing_classes + ' ' + css_class
        else:
            classes = css_class
            
        # Etapa 4: Re-renderizar o Widget
        # Retorna o campo (value) renderizado como um widget HTML,
        # injetando os novos 'attrs' (atributos) com as classes CSS combinadas.
        return value.as_widget(attrs={'class': classes})
    
    # Fallback: Se o 'value' não for um campo de formulário,
    # retorna o valor original sem alterá-lo, evitando que o site quebre.
    return value