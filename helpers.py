from typing import Optional

def check_bad_password(password: str) -> Optional[str]:
    if len(password) < 4:
        return "Password must be at least 4 characters."
    if ' ' in password:
        return "Password cannot contain spaces."
    return