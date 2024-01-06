from grpc_utils.database_pb2_grpc import DataBaseStub
from auth.auth import get_normal_user, get_admin_user
from database_service.session import get_grpc
from database_service.functions import (
    get_user,
    create_user,
    edit_user_info,
    edit_user_password,
    delete_user_target,
    edit_user_role
)
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status
)
from schemas import (
    BaseResponse,
    UserRegister,
    HTTPError,
    UserUpdateInfo,
    UserUpdatePassword,
    UserInfoResponse,
    UserUpdateRole,
    UserDelete,
    TokenUser
)
import logging

# Create a file handler to save logs to a file
logger = logging.getLogger('user_router.log') 
logger.setLevel(logging.DEBUG)

file_handler = logging.FileHandler('user_router.log') 
file_handler.setLevel(logging.DEBUG) 
formatter = logging.Formatter('%(asctime)s - %(levelname)s | %(message)s') 
file_handler.setFormatter(formatter) 
logger.addHandler(file_handler) 

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)s | %(message)s')
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)


router = APIRouter(prefix='/user', tags=['User'])

@router.get('/info', response_model= UserInfoResponse, responses= {404:{'model':HTTPError}, 500:{'model':HTTPError}} )
def get_user_information(current_user: TokenUser= Depends(get_normal_user), stub: DataBaseStub = Depends(get_grpc)):

    logger.debug(f'[info] Receive a get_user_informaion request [username: {current_user.username}]')

    resp ,err = get_user(current_user.username, current_user.username, stub, logger, 'info')
    if err:
        raise err
    
    return UserInfoResponse(**resp)


@router.post('/new', response_model= BaseResponse, responses= {500:{'model':HTTPError}, 409:{'model':HTTPError}} )
def create_new_user(request: UserRegister, current_user: TokenUser= Depends(get_admin_user), stub: DataBaseStub = Depends(get_grpc)):

    logger.debug(f'[new] Receive a create_new_user request [caller: {current_user.username} -new_username: {request.username}]')

    resp, _ = get_user(current_user.username, request.username, stub, logger, 'new')
    if resp:
        raise HTTPException(status_code= status.HTTP_409_CONFLICT, detail={'message': 'Username already exists', 'code': 2403})

    user_data = {
        'username': request.username,
        'password': request.password,
        'name': request.name,
        'email': request.email,
        'phone_number': request.phone_number,
        'role': request.role
    }

    resp ,err = create_user(current_user.username, user_data, stub, logger)
    if err:
        raise err

    return BaseResponse(**resp)


@router.put('/info/edit', response_model= BaseResponse, responses= {500:{'model':HTTPError}, 404:{'model':HTTPError}} )
def edit_user_information(request: UserUpdateInfo, current_user: TokenUser= Depends(get_normal_user), stub: DataBaseStub = Depends(get_grpc)):

    logger.debug(f'[edit info] Receive a edit_user_information request [username: {current_user.username}]')

    _, err = get_user(current_user.username, current_user.username, stub, logger, 'edit info')
    if err:
        raise err
    
    new_user_data = {
        'name': request.new_name,
        'email': request.new_email,
        'phone_number': request.new_phone_number
    }

    resp, err = edit_user_info(current_user.username, new_user_data, stub, logger)
    if err:
        raise err

    return BaseResponse(**resp)


@router.put('/pass/edit', response_model= BaseResponse, responses= {500:{'model':HTTPError}, 404:{'model':HTTPError}} )
def change_user_password(request: UserUpdatePassword, current_user: TokenUser= Depends(get_normal_user), stub: DataBaseStub = Depends(get_grpc)):

    logger.debug(f'[edit pass] Receive a edit_user_password request [username: {current_user.username}]')

    _, err = get_user(current_user.username, current_user.username, stub, logger, 'edit password')
    if err:
        raise err

    new_password = {
        'password': request.new_password
    }
    
    resp, err = edit_user_password(current_user.username, new_password, stub, logger)
    if err:
        raise err
    
    return BaseResponse(**resp)

@router.put('/role/edit', response_model= BaseResponse, responses= {500:{'model':HTTPError}, 404:{'model':HTTPError}} )
def change_user_role(request: UserUpdateRole, current_user: TokenUser= Depends(get_admin_user), stub: DataBaseStub = Depends(get_grpc)):

    logger.debug(f'[edit role] Receive a change_user_role request [caller: {current_user.username} -edit_username: {request.username} ]')

    _, err = get_user(current_user.username, request.username, stub, logger, 'edit password')
    if err:
        raise err
    
    new_role_data = {
        'username': request.username,
        'role': request.new_role
    }

    resp, err = edit_user_role(current_user.username, new_role_data, stub, logger)
    if err:
        raise err
    
    return BaseResponse(**resp)



@router.delete('/delete', response_model= BaseResponse, responses= {500:{'model':HTTPError}, 404:{'model':HTTPError}} )
def delete_user(request: UserDelete, current_user: TokenUser= Depends(get_admin_user), stub: DataBaseStub = Depends(get_grpc)):
    
    logger.debug(f'[delete] Receive a delete_user request [caller: {current_user.username} -delete_username: {request.username} ]')

    _, err = get_user(current_user.username, request.username, stub, logger, 'edit password')
    if err:
        raise err
    
    user_data = {
        'username': request.username
    }

    resp, err = delete_user_target(current_user.username, user_data, stub, logger)
    if err:
        raise err
    
    return BaseResponse(**resp)