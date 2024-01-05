from typing import Annotated
from fastapi import Depends, HTTPException, status, APIRouter
from fastapi.security import OAuth2PasswordRequestForm
from grpc_utils.database_pb2_grpc import DataBaseStub
from auth.auth import verify_password, create_access_token
from database_service.session import get_grpc
from cache.session import get_redis_cache
import grpc_utils.database_pb2 as pb2
from schemas import Token, HTTPError
from redis import Redis
from cache.functions import set_token
import logging
from grpc._channel import _InactiveRpcError

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

    if form_data.scopes and 'admin' in form_data.scopes :
        scopes = ['admin', 'user']

    elif form_data.scopes and 'user' in form_data.scopes:
        scopes = ['user']

    else : 

        logger.debug(f'[login] Reject request due a Unkown Scopes [username: {form_data.username} -scopes: {form_data.scopes}]')
        raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail= {'code': 2001, 'message': "Unkown Scopes"},
        )

    try:

        resp_user = stub.GetUser(pb2.RequestUserInfo(**{'username': form_data.username}))

    except _InactiveRpcError as InactiveRpcError:
        logger.error(f"[login] API-service can't connect to grpc host (user:{form_data.username} -error: {InactiveRpcError})")
        raise HTTPException(status_code= status.HTTP_500_INTERNAL_SERVER_ERROR, detail={'code': 2002, 'message': "API-service can't connect to grpc host"})

    except Exception as e :
        logger.error(f'[login] Error in grpc connection (user:{form_data.username} -error: {e})')
        raise HTTPException(status_code= status.HTTP_500_INTERNAL_SERVER_ERROR, detail={'code': 2003, 'message': "Error in grpc connection"})

    if resp_user.code != 1200:
        logger.debug(f'[login] User not found [username: {form_data.username}]')
        raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED, detail={'code': 2401,'message':'Incorrect username or password'})

    if resp_user.data.role.lower() in scopes:
        logger.debug(f'[login] Not enough permissions [username: {form_data.username}]')
        raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED, detail= {'code': 2402, 'message': 'Not enough permissions'})

    check_password = verify_password(resp_user.data.password, form_data.password )

    if not check_password:
        logger.debug(f'[login] Incorrect username or password [username: {form_data.username}]')
        raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED, detail= {'code': 2403, 'message': "Incorrect username or password"})
    
    access_token = create_access_token(
        data={"user": resp_user.data.user_id, 'role': resp_user.data.role, "scopes": scopes}
    )

    set_token(resp_user.data.user_id, access_token, cache_db)
    
    return {"access_token": access_token, "token_type": "bearer"}



