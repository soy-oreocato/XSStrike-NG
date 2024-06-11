# Reemplazar cada caracter especial con su entidad HTML correspondiente
def convert_to_html_entities(text):
    
    html_entities = {
        '<': '&lt;',
        '>': '&gt;',
        '&': '&amp;',
        '"': '&quot;',
        "'": '&apos;'
    }

    for char, entity in html_entities.items():
        text = text.replace(char, entity)
    
    return text