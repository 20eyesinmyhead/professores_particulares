from django import template

# Cria uma instância da biblioteca de templates
register = template.Library()

@register.filter(name='add_class')
def add_class(value, css_class):
    """
    Adiciona uma classe CSS ao campo do formulário (Widget).
    
    Uso no template: {{ field|add_class:"minha-classe" }}
    """
    # Verifica se o campo possui um widget
    if hasattr(value, 'field') and hasattr(value.field.widget, 'attrs'):
        # Obtém as classes CSS existentes ou inicia uma string vazia
        existing_classes = value.field.widget.attrs.get('class', '')
        
        # Concatena a nova classe, garantindo que haja um espaço, se necessário
        if existing_classes:
            classes = existing_classes + ' ' + css_class
        else:
            classes = css_class
            
        # Define o atributo 'class' com as novas classes
        return value.as_widget(attrs={'class': classes})
    
    # Se não for um campo de formulário ou não tiver o atributo 'attrs', retorna o valor original
    return value