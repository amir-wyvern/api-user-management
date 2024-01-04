from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from enum import Enum
import re


class PhoneNumberStr(str):
    @classmethod
    def __get_pydantic_json_schema__(cls, model, context):
        return {'type': 'string', 'format': 'phonenumber', 'example': '+98-9151234567'}
    
    @classmethod
    def __get_validators__(cls):
        yield cls.validate
    
    @classmethod
    def validate(cls, v, x):
        if not re.match(r"^\+\d{1,3}-\d{6,12}$", v):
            raise ValueError("Not a valid phone number")
        return v

# ========== Base ========== 

class BaseResponse(BaseModel):

    message: str
    code: int

class HTTPError(BaseModel):

    message: str 
    internal_code: str

    class Config:
        json_schema_extra = {
            "example": {"detail": "HTTPException raised.", 'internal_code':1001},
        }
        

# ========== User ========== 

class UserRole(str ,Enum):

    ADMIN = 'ADMIN'
    USER = 'USER'

    
class UserInfoResponse(BaseModel):

    username: str
    name: str 
    email:  EmailStr
    phone_number: PhoneNumberStr
    role: UserRole

    class Config:
        from_attributes = True

class UserRegister(BaseModel):

    username : str
    password: str
    name : str
    email: Optional[EmailStr] = Field(default=None)
    phone_number: PhoneNumberStr
    role: UserRole


class UserUpdatePassword(BaseModel):

    username : str
    new_password: str
    
class UserUpdateRole(BaseModel):

    username : str
    new_role: UserRole
    
class UserUpdateInfo(BaseModel):

    username : str
    new_email: Optional[EmailStr]
    new_phone_number: Optional[PhoneNumberStr] 
    new_name: Optional[str] 


class UserDelete(BaseModel):

    username : str


# ========== Auth ========== 


class UserAuthResponse(BaseModel):

    access_token: str
    type_token: str


class Token(BaseModel):
    
    access_token: str
    token_type: str

class TokenData(BaseModel):
    user_id: int | None = None
    role: UserRole | None = None
    scopes: List[str] = []

class TokenUser(BaseModel):

    user_id: int
    role: UserRole