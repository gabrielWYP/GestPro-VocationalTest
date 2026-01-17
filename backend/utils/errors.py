"""
Manejo de errores personalizados
"""

class VocationalTestError(Exception):
    """Error base de la aplicación"""
    pass


class DatabaseError(VocationalTestError):
    """Error de base de datos"""
    pass


class ValidationError(VocationalTestError):
    """Error de validación"""
    pass


class NotFoundError(VocationalTestError):
    """Recurso no encontrado"""
    pass
