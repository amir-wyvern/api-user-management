from fastapi.security import OAuth2PasswordBearer, SecurityScopes
from jose import jwt

from passlib.context import CryptContext
from typing import Annotated
from pydantic import ValidationError
from jose import JWTError, jwt
from schemas import TokenUser, UserRole
from fastapi import (
  Depends,
  HTTPException,
  status,
  Security
) 
import os
from schemas import TokenData
from redis import Redis
from cache.session import get_redis_cache
from cache.functions import get_token


OAUTH2_SECRET_KEY = os.getenv('OAUTH2_SECRET_KEY')
OAUTH2_ALGORITHM = os.getenv('OAUTH2_ALGORITHM')

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/auth/login",
    scopes={"USER": "normal user", "ADMIN": "administrator user"},
)

def verify_password(plain_password, hashed_password):

    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict):
    to_encode = data.copy()
    encoded_jwt = jwt.encode(to_encode, OAUTH2_SECRET_KEY, algorithm=OAUTH2_ALGORITHM)
    return encoded_jwt


async def get_current_user(security_scopes: SecurityScopes, token: Annotated[str, Depends(oauth2_scheme)], cache_db: Redis= Depends(get_redis_cache) ):
    
    if security_scopes.scopes:
        authenticate_value = f'Bearer scope="{security_scopes.scope_str}"'

    else:
        authenticate_value = "Bearer"

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": authenticate_value},
    )

    try:
        payload = jwt.decode(token, OAUTH2_SECRET_KEY, algorithms=[OAUTH2_ALGORITHM])
        user_id: int = payload.get("user_id")
        
        token = get_token(user_id, cache_db)

        if token is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token is expired",
                headers={"WWW-Authenticate": authenticate_value},
            )

        scopes = payload.get("scopes", [])
        role = payload.get("role", None)

        username = payload.get("username", None)
        token_data = TokenData(user_id= user_id, role= role, username= username, scopes= scopes)
            
    except (JWTError, ValidationError):
        raise credentials_exception

    except HTTPException as e:
        raise e

    for scope in security_scopes.scopes:
        if scope not in token_data.scopes:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not enough permissions",
                headers={"WWW-Authenticate": authenticate_value},
            )
        
    return TokenUser(user_id=user_id, role=role, username= username)


async def get_normal_user(current_user: Annotated[TokenUser, Security(get_current_user, scopes=["USER"])]):
    
    return current_user

async def get_admin_user(current_user: Annotated[TokenUser, Security(get_current_user, scopes=["ADMIN", "USER"])]):
        
    return current_user

