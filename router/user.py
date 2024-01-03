from fastapi import (
    APIRouter,
    Depends
)
from schemas import (
    BaseResponse,
    UserRegister,
    HTTPError,
    UserUpdateInfo,
    UserInfoResponse
)
from database_service.session import get_grpc
from grpc_utils.database_pb2_grpc import DataBaseStub
import grpc_utils.database_pb2 as pb2

router = APIRouter(prefix='/user', tags=['User'])

@router.get('/info', response_model= UserInfoResponse, responses= {404:{'model':HTTPError}, 403:{'model':HTTPError}} )
def create_new_user(username: str, stub: DataBaseStub = Depends(get_grpc)):

    data = {
            'name': 'test',
            'username': 'test',
            'email': 'test',
            'phone_number': 'test',
            'role': 'admin'
        }
    return UserInfoResponse(**data)

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
    
    stub.NewUser(pb2.RequestNewUser(**data))
    
    return BaseResponse(message= 'message test', code= 1200)

@router.put('/info/edit', response_model= BaseResponse, responses= {404:{'model':HTTPError}, 403:{'model':HTTPError}} )
def edit_user_information(request: UserUpdateInfo, stub: DataBaseStub = Depends(get_grpc)):

    return BaseResponse(message= 'message test', code= 1200)

@router.put('/pass/edit', response_model= BaseResponse, responses= {404:{'model':HTTPError}, 403:{'model':HTTPError}} )
def change_user_password(request: UserUpdateInfo, stub: DataBaseStub = Depends(get_grpc)):

    return BaseResponse(message= 'message test', code= 1200)

@router.put('/role/edit', response_model= BaseResponse, responses= {404:{'model':HTTPError}, 403:{'model':HTTPError}} )
def change_user_role(request: UserUpdateInfo, stub: DataBaseStub = Depends(get_grpc)):

    return BaseResponse(message= 'message test', code= 1200)

@router.delete('/delete', response_model= BaseResponse, responses= {404:{'model':HTTPError}, 403:{'model':HTTPError}} )
def delete_user(request: UserUpdateInfo, stub: DataBaseStub = Depends(get_grpc)):

    return BaseResponse(message= 'message test', code= 1200)

