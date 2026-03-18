def validate_password(password: str) -> bool:
    if len(password) < 8:
        return False
    if not any(c.isupper() for c in password):
        return False
    if not any(c.isdigit() for c in password):
        return False
    if not any(c in "!@#$%^&*()-_=+" for c in password):
        return False
    return True

def validate_email(email: str) -> bool:
    import re
    return re.match(r"[^@]+@[^@]+\.[^@]+", email) is not None

def validate_role(role: str) -> bool:
    return role in ['patient', 'clinician', 'admin']

def sanitize_input(input_str: str, max_length: int = 100) -> str:
    import re
    from html import escape
    # Remove HTML tags
    cleaned = re.sub(r'<[^>]+>', '', input_str)
    # Escape remaining special characters
    return escape(cleaned[:max_length])

def validate_date(date_str: str) -> bool:
    from datetime import datetime
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except ValueError:
        return False

def validate_min_length(value: str, min_length: int) -> bool:
    return len(value) >= min_length

def validate_max_length(value: str, max_length: int) -> bool:
    return len(value) <= max_length

def validate_numeric(value: str) -> bool:
    return value.isdigit()

def validate_required(value: str) -> bool:
    return bool(value.strip())

def validate_combined(data: dict) -> bool:
    return validate_email(data.get('email', '')) and validate_password(data.get('password', ''))
