def sanitize_sql_name(name):
    """Sanitize input name for SQL usage by removing special characters."""
    import re
    # Remove símbolos especiais e substitui por underscore
    # Mantém apenas letras, números e underscores
    sanitized = re.sub(r'[/\-;()\'"\[\]{}<>.,!@#$%^&*+=|\\~`?:]', '_', name.lower())
    # Remove múltiplos underscores consecutivos
    sanitized = re.sub(r'_+', '_', sanitized)
    # Remove underscores no início e fim
    sanitized = sanitized.strip('_')
    return sanitized


def get_sql_type(dtype):
    """Mapeia tipos de dados do pandas para tipos SQL."""
    import pandas as pd
    
    if pd.api.types.is_integer_dtype(dtype):
        return "INT"
    elif pd.api.types.is_float_dtype(dtype):
        return "FLOAT"
    elif pd.api.types.is_datetime64_any_dtype(dtype):
        return "DATETIME"
    elif pd.api.types.is_bool_dtype(dtype):
        return "BOOLEAN"
    elif pd.api.types.is_object_dtype(dtype):
        return "VARCHAR(255)"
    else:
        return "TEXT"