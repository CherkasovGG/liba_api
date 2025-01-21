import bcrypt


def hash_password(password: str) -> bytes:
    """Шифрование пароля"""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode(), salt)


def check_password(password: str, hashed_password: bytes) -> bool:
    """Проверка совпадения пароля"""
    return bcrypt.checkpw(password.encode(), hashed_password)
