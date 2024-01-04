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

router = APIRouter(prefix='/user', tags=['User'])

@router.get('/info', response_model= UserInfoResponse, responses= {404:{'model':HTTPError}, 403:{'model':HTTPError}} )
def create_new_user(username: str, stub: DataBaseStub = Depends(get_grpc)):

    data = {
        'username': username
    }

    resp = stub.GetUser(pb2.RequestGetUser(**data))
    
    if resp.code != 1200:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail={'message': resp.message, 'internal_code': resp.code})

    resp_user = {
        'username': resp.username,
        'name': resp.name,
        'email': resp.email,
        'phone_number': resp.phone_number, 
        'role': resp.role
    }
    return UserInfoResponse(**resp_user)


@router.post('/new', response_model= BaseResponse, responses= {404:{'model':HTTPError}, 403:{'model':HTTPError}} )
def create_new_user(request: UserRegister, stub: DataBaseStub = Depends(get_grpc)):

    data = {
        'name': request.name,
        'username': request.username,
        'password': request.password,
        'email': request.email,
        'phone_number': request.phone_number,
        'role': request.role
    }
    
    resp = stub.NewUser(pb2.RequestNewUser(**data))

    if resp.code != 1200:
        raise HTTPException(status_code= status.HTTP_403_FORBIDDEN, detail={'message': resp.message, 'internal_code': resp.code})

    return BaseResponse(message= 'message test', code= 1200)


@router.put('/info/edit', response_model= BaseResponse, responses= {404:{'model':HTTPError}, 403:{'model':HTTPError}} )
def edit_user_information(request: UserUpdateInfo, stub: DataBaseStub = Depends(get_grpc)):

    data = {
        'username': request.username,
        'name': request.new_name,
        'email': request.new_email,
        'phone_number': request.new_phone_number
    }

    resp = stub.ModifyUserInfo(pb2.RequestModifyUserInfo(**data))
    if resp.code != 1200:
        raise HTTPException(status_code= status.HTTP_403_FORBIDDEN, detail={'message': resp.message, 'internal_code': resp.code})

    return BaseResponse(message= 'message test', code= 1200) 


@router.put('/pass/edit', response_model= BaseResponse, responses= {404:{'model':HTTPError}, 403:{'model':HTTPError}} )
def change_user_password(request: UserUpdatePassword, stub: DataBaseStub = Depends(get_grpc)):

    data = {
        'username': request.username,
        'password': request.new_password
    }
    
    resp = stub.ModifyUserPassword(pb2.RequestModifyUserPassword(**data))
    if resp.code != 1200:
        raise HTTPException(status_code= status.HTTP_403_FORBIDDEN, detail={'message': resp.message, 'internal_code': resp.code})

    return BaseResponse(message= 'message test', code= 1200)

@router.put('/role/edit', response_model= BaseResponse, responses= {404:{'model':HTTPError}, 403:{'model':HTTPError}} )
def change_user_role(request: UserUpdateRole, stub: DataBaseStub = Depends(get_grpc)):

    data = {
        'username': request.username,
        'role': request.new_role
    }

    resp = stub.ModifyUserRole(pb2.RequestModifyUserRole(**data))
    if resp.code != 1200:
        raise HTTPException(status_code= status.HTTP_403_FORBIDDEN, detail={'message': resp.message, 'internal_code': resp.code})

    return BaseResponse(message= 'message test', code= 1200)


@router.delete('/delete', response_model= BaseResponse, responses= {404:{'model':HTTPError}, 403:{'model':HTTPError}} )
def delete_user(request: UserDelete, stub: DataBaseStub = Depends(get_grpc)):
    
    data = {
        'username': request.username
    }

    resp = stub.DeleteUser(pb2.RequestDeleteUser(**data))
    if resp.code != 1200:
        raise HTTPException(status_code= status.HTTP_403_FORBIDDEN, detail={'message': resp.message, 'internal_code': resp.code})

    return BaseResponse(message= 'message test', code= 1200)

