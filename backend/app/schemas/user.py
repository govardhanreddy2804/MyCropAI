from pydantic import BaseModel


class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str = Field(min_length=8)