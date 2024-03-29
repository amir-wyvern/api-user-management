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
    code: str

    class Config:
        json_schema_extra = {
            "example": {"detail": "HTTPException raised.", 'code':1001},
        }
        

# ========== User ========== 

class UserRole(str ,Enum):

    ADMIN = 'ADMIN'
    USER = 'USER'

    
class UserInfoResponse(BaseModel):

    username: str
    name: str 
    email:  Optional[EmailStr] = Field(default=None)
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

    new_password: str
    
class UserUpdateRole(BaseModel):

    username : str
    new_role: UserRole
    
class UserUpdateInfo(BaseModel):

    new_email: Optional[EmailStr] = Field(default=None)
    new_phone_number: Optional[PhoneNumberStr] = Field(default=None)
    new_name: Optional[str] = Field(default=None)


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
    user_id: int 
    username: str 
    role: UserRole 
    scopes: List[str] = []

class TokenUser(BaseModel):

    user_id: int
    username: str
    role: UserRole