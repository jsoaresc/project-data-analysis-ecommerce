def formatar_categoria(texto):
    if not isinstance(texto, str):
        return "Não Informada"
    
    texto = texto.replace("_", " ").title()
    return texto