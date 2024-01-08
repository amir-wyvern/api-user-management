from fastapi import Depends, HTTPException, status, APIRouter
from auth.auth import verify_password, create_access_token
from fastapi.security import OAuth2PasswordRequestForm
from grpc_utils.database_pb2_grpc import DataBaseStub
from database_service.functions import get_user
from database_service.session import get_grpc
from grpc._channel import _InactiveRpcError
from cache.session import get_redis_cache
import grpc_utils.database_pb2 as pb2
from cache.functions import set_token
from schemas import Token, HTTPError
from datetime import datetime, timedelta
from typing import Annotated
from redis import Redis
import logging

# Create a file handler to save logs to a file
logger = logging.getLogger('auth_router.log') 
logger.setLevel(logging.DEBUG)

file_handler = logging.FileHandler('auth_router.log') 
file_handler.setLevel(logging.DEBUG) 
formatter = logging.Formatter('%(asctime)s - %(levelname)s | %(message)s') 
file_handler.setFormatter(formatter) 
logger.addHandler(file_handler) 

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)s | %(message)s')
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

router = APIRouter(prefix='/auth', tags=['Auth'])

@router.post("/login", response_model=Token, responses= {401:{'model':HTTPError}, 500:{'model':HTTPError}})
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], stub: DataBaseStub= Depends(get_grpc), cache_db: Redis= Depends(get_redis_cache)):
    
    logger.debug(f'[login] Receive a login request [username: {form_data.username} -scopes: {form_data.scopes}]')
    
    if form_data.scopes and 'ADMIN' in form_data.scopes :
        scopes = ['ADMIN', 'USER']

    elif form_data.scopes and 'USER' in form_data.scopes:
        scopes = ['USER']

    else : 

        logger.debug(f'[login] Reject request due a Unkown Scopes [username: {form_data.username} -scopes: {form_data.scopes}]')
        raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail= {'code': 2001, 'message': "Unkown Scopes"},
        )

    resp_user, err = get_user(form_data.username, form_data.username, stub, logger, 'login')
    if err:
        raise err
    
    if resp_user['role'] not in scopes:
        logger.debug(f'[login] Not enough permissions [username: {form_data.username}]')
        raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED, detail= {'code': 2409, 'message': 'Not enough permissions'})

    check_password = verify_password(form_data.password, resp_user['password'] )

    if not check_password:
        logger.debug(f'[login] Incorrect username or password [username: {form_data.username}]')
        raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED, detail= {'code': 2408, 'message': "Incorrect username or password"})
    
    access_token = create_access_token(
        data={
            "user_id": resp_user['user_id'],
            'username': resp_user['username'],
            'role': resp_user['role'],
            'exp': datetime.utcnow() + timedelta(days=7),
            "scopes": scopes
            }
    )

    set_token(resp_user['user_id'], access_token, cache_db)
    
    return {"access_token": access_token, "token_type": "bearer"}

