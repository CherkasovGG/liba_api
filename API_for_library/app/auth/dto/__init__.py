from pydantic import BaseModel, EmailStr


class TokenRequestDTO(BaseModel):
    email: EmailStr
    password: str


class TokenResponseDTO(BaseModel):
    access_token: str
    token_type: str = "baerer"


class TokenDTO(BaseModel):
    token: str
