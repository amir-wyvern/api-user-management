from typing import Annotated
from fastapi import Depends, HTTPException, status, APIRouter
from fastapi.security import OAuth2PasswordRequestForm
from schemas import Token
from auth.auth import verify_password, create_access_token
from database_service.session import get_grpc
from grpc_utils.database_pb2_grpc import DataBaseStub
import grpc_utils.database_pb2 as pb2
import logging

# Create a file handler to save logs to a file
logger = logging.getLogger('auth_router.log') 
logger.setLevel(logging.INFO)

file_handler = logging.FileHandler('auth_router.log') 
file_handler.setLevel(logging.INFO) 
formatter = logging.Formatter('%(asctime)s - %(levelname)s | %(message)s') 
file_handler.setFormatter(formatter) 
logger.addHandler(file_handler) 

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s | %(message)s')
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

router = APIRouter(prefix='/auth', tags=['Auth'])

@router.post("/login", response_model=Token)
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], stub: DataBaseStub= Depends(get_grpc)):
    
    if form_data.scopes and 'admin' in form_data.scopes :
        
        scope = 'admin'

    elif form_data.scopes and 'user' in form_data.scopes:
        
        scope = 'user'

    else : 
        return HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unkown Scopes",
        )
    try:

        resp_user = stub.GetUser(pb2.RequestGetUser(**{'username': form_data.username}))

        if resp_user.code != 1200 :
            return HTTPException(status_code= status.HTTP_401_UNAUTHORIZED, detail='Incorrect username or password')


    except Exception as e:
        logger.error(f'[login] error in grpc connection (user:{form_data.username} -error: {e})')
        return HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail='check the logs for more info')
    
    if resp_user.data.role.lower() == scope:
        return HTTPException(status_code= status.HTTP_401_UNAUTHORIZED, detail='Incorrect username or password')
    
    check_password = verify_password(resp_user.data.password, form_data.password )

    if not check_password:
        return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")
    
    access_token = create_access_token(
        data={"user": resp_user.data.user_id, 'role': resp_user.data.role, "scopes": scope},
    )

    return {"access_token": access_token, "token_type": "bearer"}



