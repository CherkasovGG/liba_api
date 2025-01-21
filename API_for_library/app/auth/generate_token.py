from pathlib import Path

import jwt
from pydantic import BaseModel
from pydantic_settings import BaseSettings

from datetime import datetime, timedelta

BASE_DIR = Path(__file__).parent.parent


class AuthJWT(BaseModel):
    private_key_path: Path = BASE_DIR / "certifications" / "jwt-private.key"
    public_key_path: Path = BASE_DIR / "certifications" / "jwt-public.key"
    algorithm: str = "RS256"
    access_token_exipre_minutes: int = 3


class Settings(BaseSettings):
    auth_jwt: AuthJWT = AuthJWT()


settings = Settings()


class JWTService:
    def __init__(
        self,
        private_key_path: Path = settings.auth_jwt.private_key_path,
        public_key_path: Path = settings.auth_jwt.public_key_path,
        algorithm: str = settings.auth_jwt.algorithm,
        access_token_expire_minutes: int = settings.auth_jwt.access_token_exipre_minutes,
    ):
        self.private_key = private_key_path.read_text()
        self.public_key = public_key_path.read_text()
        self.algorithm = algorithm
        self.access_token_expire_minutes = access_token_expire_minutes

    def encode_jwt(self, payload: dict) -> str:
        """
        Создаем JWT токен.
        """
        if "exp" not in payload:
            payload["exp"] = datetime.now() + timedelta(
                minutes=self.access_token_expire_minutes
            )
        token = jwt.encode(payload, self.private_key, algorithm=self.algorithm)
        return token

    def decode_jwt(self, token: str) -> dict:
        """
        Декодируем JWT токен.
        """
        try:
            decoded = jwt.decode(token, self.public_key, algorithms=[self.algorithm])
            return decoded
        except jwt.ExpiredSignatureError:
            raise ValueError("Токен истек")
        except jwt.InvalidTokenError:
            raise ValueError("Недействительный токен")
