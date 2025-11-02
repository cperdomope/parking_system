"""
Utilidades de formateo para el sistema de parqueaderos.

Este módulo contiene funciones auxiliares para formatear datos
de forma consistente en toda la aplicación.
"""


def format_numero_parqueadero(numero):
    """
    Formatea el número de parqueadero para mostrar.

    Después de la migración v2.0.3, numero_parqueadero puede ser:
    - VARCHAR: "P-001", "P-002", etc. (formato nuevo)
    - INTEGER: 1, 2, 3, etc. (compatibilidad con datos antiguos)

    Args:
        numero: Número de parqueadero (str o int)

    Returns:
        str: Número formateado como "P-001", "P-002", etc.

    Examples:
        >>> format_numero_parqueadero("P-001")
        'P-001'
        >>> format_numero_parqueadero(1)
        'P-001'
        >>> format_numero_parqueadero("125")
        'P-125'
    """
    if numero is None:
        return "N/A"

    # Si ya es string con formato P-XXX, retornar directamente
    if isinstance(numero, str):
        if numero.startswith('P-'):
            return numero
        else:
            # Es string numérico ("1", "25", etc.)
            try:
                numero_int = int(numero)
                return f"P-{numero_int:03d}"
            except ValueError:
                # Si no se puede convertir, retornar tal cual
                return numero

    # Si es entero, formatear con ceros a la izquierda
    if isinstance(numero, int):
        return f"P-{numero:03d}"

    # Caso inesperado, retornar como string
    return str(numero)
