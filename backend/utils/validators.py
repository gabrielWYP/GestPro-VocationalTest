"""
Validaciones reutilizables
"""
import re


def validate_email(email: str) -> bool:
    """Validar formato de email"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_name(name: str) -> bool:
    """Validar que el nombre no esté vacío"""
    return name and len(name.strip()) > 0


def validate_date(date_str: str) -> bool:
    """Validar formato de fecha (YYYY-MM-DD)"""
    pattern = r'^\d{4}-\d{2}-\d{2}$'
    return re.match(pattern, date_str) is not None


def validate_time(time_str: str) -> bool:
    """Validar formato de hora (HH:MM)"""
    pattern = r'^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$'
    return re.match(pattern, time_str) is not None
