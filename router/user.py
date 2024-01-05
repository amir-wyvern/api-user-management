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
    UserDelete
)
from database_service.session import get_grpc
from grpc_utils.database_pb2_grpc import DataBaseStub
import grpc_utils.database_pb2 as pb2
from grpc._channel import _InactiveRpcError
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
def get_user_information(username: str, stub: DataBaseStub = Depends(get_grpc)):

    logger.debug(f'[info] Receive a get_user_informaion request [username: {username}]')

    data = {
        'username': username
    }
    
    try:

        resp = stub.GetUser(pb2.RequestGetUser(**data))

    except _InactiveRpcError as InactiveRpcError:
        logger.error(f"[info] API-service can't connect to grpc host [user:{username} -error: {InactiveRpcError}]")
        raise HTTPException(status_code= status.HTTP_500_INTERNAL_SERVER_ERROR, detail={'code': 2002, 'message': "API-service can't connect to grpc host"})

    except Exception as e :
        logger.error(f'[info] Error in grpc connection [user:{username} -error: {e}]')
        raise HTTPException(status_code= status.HTTP_500_INTERNAL_SERVER_ERROR, detail={'code': 2003, 'message': "Error in grpc connection"})

    if resp.code == 1401:
        logger.debug(f'[info] Username is not found [username: {username}]')
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail={'message': 'Username is not found', 'code': 2401})

    elif resp.code != 1200:
        logger.debug(f'[info] error in database service [username: {username} -err_msg: {resp.message} -err_code: {resp.code}]')
        raise HTTPException(status_code= status.HTTP_500_INTERNAL_SERVER_ERROR, detail={'message': 'Contact to support!', 'code': resp.code})

    resp_user = {
        'username': resp.username,
        'name': resp.name,
        'email': resp.email,
        'phone_number': resp.phone_number, 
        'role': resp.role
    }
    return UserInfoResponse(**resp_user)


@router.post('/new', response_model= BaseResponse, responses= {500:{'model':HTTPError}, 409:{'model':HTTPError}} )
def create_new_user(request: UserRegister, stub: DataBaseStub = Depends(get_grpc)):

    logger.debug(f'[new] Receive a create_new_user request [username: {request.username}]')

    data = {
        'name': request.name,
        'username': request.username,
        'password': request.password,
        'email': request.email,
        'phone_number': request.phone_number,
        'role': request.role
    }
    
    try:

        resp = stub.NewUser(pb2.RequestNewUser(**data))

    except _InactiveRpcError as InactiveRpcError:
        logger.error(f"[new] API-service can't connect to grpc host [user:{request.username} -error: {InactiveRpcError}]")
        raise HTTPException(status_code= status.HTTP_500_INTERNAL_SERVER_ERROR, detail={'code': 2002, 'message': "API-service can't connect to grpc host"})

    except Exception as e :
        logger.error(f'[new] Error in grpc connection [user:{request.username} -error: {e}]')
        raise HTTPException(status_code= status.HTTP_500_INTERNAL_SERVER_ERROR, detail={'code': 2003, 'message': "Error in grpc connection"})

    if resp.code == 1403:
        logger.debug(f'[new] Username already exists [username: {request.username}]')
        raise HTTPException(status_code= status.HTTP_409_CONFLICT, detail={'message': 'Username already exists', 'code': 2403})

    if resp.code != 1200:
        logger.debug(f'[new] error in database service [username: {request.username} -err_msg: {resp.message} -err_code: {resp.code}]')
        raise HTTPException(status_code= status.HTTP_500_INTERNAL_SERVER_ERROR, detail={'message': 'Contact to support!', 'code': resp.code})

    return BaseResponse(message= 'message test', code= 1200)


@router.put('/info/edit', response_model= BaseResponse, responses= {500:{'model':HTTPError}, 400:{'model':HTTPError}} )
def edit_user_information(request: UserUpdateInfo, stub: DataBaseStub = Depends(get_grpc)):

    logger.debug(f'[new] Receive a edit_user_information request [username: {request.username}]')

    data = {
        'username': request.username,
        'name': request.new_name,
        'email': request.new_email,
        'phone_number': request.new_phone_number
    }

    try:

        resp = stub.ModifyUserInfo(pb2.RequestModifyUserInfo(**data))

    except _InactiveRpcError as InactiveRpcError:
        logger.error(f"[edit info] API-service can't connect to grpc host [user:{request.username} -error: {InactiveRpcError}]")
        raise HTTPException(status_code= status.HTTP_500_INTERNAL_SERVER_ERROR, detail={'code': 2002, 'message': "API-service can't connect to grpc host"})

    except Exception as e :
        logger.error(f'[edit info] Error in grpc connection [user:{request.username} -error: {e}]')
        raise HTTPException(status_code= status.HTTP_500_INTERNAL_SERVER_ERROR, detail={'code': 2003, 'message': "Error in grpc connection"})
    
    if resp.code == 1401:
        logger.debug(f'[edit info] Username is not found [username: {request.username}]')
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail={'message': 'Username is not found', 'code': 2401})

    if resp.code != 1200:
        logger.debug(f'[edit info] error in database service [username: {request.username} -err_msg: {resp.message} -err_code: {resp.code}]')
        raise HTTPException(status_code= status.HTTP_500_INTERNAL_SERVER_ERROR, detail={'message': 'Contact to support!', 'code': resp.code})

    return BaseResponse(message= 'message test', code= 1200) 


@router.put('/pass/edit', response_model= BaseResponse, responses= {404:{'model':HTTPError}, 403:{'model':HTTPError}} )
def change_user_password(request: UserUpdatePassword, stub: DataBaseStub = Depends(get_grpc)):

    data = {
        'username': request.username,
        'password': request.new_password
    }
    
    try:

        resp = stub.ModifyUserPassword(pb2.RequestModifyUserPassword(**data))

    except _InactiveRpcError as InactiveRpcError:
        logger.error(f"[edit pass] API-service can't connect to grpc host [user:{request.username} -error: {InactiveRpcError}]")
        raise HTTPException(status_code= status.HTTP_500_INTERNAL_SERVER_ERROR, detail={'code': 2002, 'message': "API-service can't connect to grpc host"})

    except Exception as e :
        logger.error(f'[edit pass] Error in grpc connection [user:{request.username} -error: {e}]')
        raise HTTPException(status_code= status.HTTP_500_INTERNAL_SERVER_ERROR, detail={'code': 2003, 'message': "Error in grpc connection"})

    if resp.code == 1401:
        logger.debug(f'[edit pass] Username is not found [username: {request.username}]')
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail={'message': 'Username is not found', 'code': 2401})

    if resp.code != 1200:
        logger.debug(f'[edit pass] error in database service [username: {request.username} -err_msg: {resp.message} -err_code: {resp.code}]')
        raise HTTPException(status_code= status.HTTP_500_INTERNAL_SERVER_ERROR, detail={'message': 'Contact to support!', 'code': resp.code})

    return BaseResponse(message= 'message test', code= 1200)

@router.put('/role/edit', response_model= BaseResponse, responses= {404:{'model':HTTPError}, 403:{'model':HTTPError}} )
def change_user_role(request: UserUpdateRole, stub: DataBaseStub = Depends(get_grpc)):

    data = {
        'username': request.username,
        'role': request.new_role
    }

    try:

        resp = stub.ModifyUserRole(pb2.RequestModifyUserRole(**data))
    
    except _InactiveRpcError as InactiveRpcError:
        logger.error(f"[edit role] API-service can't connect to grpc host [user:{request.username} -error: {InactiveRpcError}]")
        raise HTTPException(status_code= status.HTTP_500_INTERNAL_SERVER_ERROR, detail={'code': 2002, 'message': "API-service can't connect to grpc host"})

    except Exception as e :
        logger.error(f'[edit role] Error in grpc connection [user:{request.username} -error: {e}]')
        raise HTTPException(status_code= status.HTTP_500_INTERNAL_SERVER_ERROR, detail={'code': 2003, 'message': "Error in grpc connection"})

    if resp.code == 1401:
        logger.debug(f'[edit role] Username is not found [username: {request.username}]')
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail={'message': 'Username is not found', 'code': 2401})

    if resp.code != 1200:
        logger.debug(f'[edit role] error in database service [username: {request.username} -err_msg: {resp.message} -err_code: {resp.code}]')
        raise HTTPException(status_code= status.HTTP_500_INTERNAL_SERVER_ERROR, detail={'message': 'Contact to support!', 'code': resp.code})

    return BaseResponse(message= 'message test', code= 1200)


@router.delete('/delete', response_model= BaseResponse, responses= {404:{'model':HTTPError}, 403:{'model':HTTPError}} )
def delete_user(request: UserDelete, stub: DataBaseStub = Depends(get_grpc)):
    
    data = {
        'username': request.username
    }

    try:

        resp = stub.DeleteUser(pb2.RequestDeleteUser(**data))

    except _InactiveRpcError as InactiveRpcError:
        logger.error(f"[delete] API-service can't connect to grpc host [user:{request.username} -error: {InactiveRpcError}]")
        raise HTTPException(status_code= status.HTTP_500_INTERNAL_SERVER_ERROR, detail={'code': 2002, 'message': "API-service can't connect to grpc host"})

    except Exception as e :
        logger.error(f'[delete] Error in grpc connection [user:{request.username} -error: {e}]')
        raise HTTPException(status_code= status.HTTP_500_INTERNAL_SERVER_ERROR, detail={'code': 2003, 'message': "Error in grpc connection"})

    if resp.code == 1401:
        logger.debug(f'[delete] Username is not found [username: {request.username}]')
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail={'message': 'Username is not found', 'code': 2401})

    if resp.code != 1200:
        logger.debug(f'[delete] error in database service [username: {request.username} -err_msg: {resp.message} -err_code: {resp.code}]')
        raise HTTPException(status_code= status.HTTP_500_INTERNAL_SERVER_ERROR, detail={'message': 'Contact to support!', 'code': resp.code})

    return BaseResponse(message= 'message test', code= 1200)
