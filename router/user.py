from fastapi import (
    APIRouter
)
from schemas import (
    BaseResponse,
    UserRegister,
    HTTPError,
    UserUpdateInfo,
    UserInfoResponse
)
import grpc_utils.database_pb2 as pb2
import grpc
import grpc_utils.database_pb2_grpc as pb2_grpc
import os 

router = APIRouter(prefix='/user', tags=['User'])

PORT = os.getenv("GRPC_PORT")
HOST = os.getenv("GRPC_HOST")

chanel = grpc.insecure_channel(f'{HOST}:{PORT}')
stub = pb2_grpc.DataBaseStub(chanel)
@router.get('/info', response_model= UserInfoResponse, responses= {404:{'model':HTTPError}, 403:{'model':HTTPError}} )
def create_new_user(username: str):

    data = {
            'name': 'test',
            'username': 'test',
            'email': 'test',
            'phone_number': 'test',
            'role': 'admin'
        }
    return UserInfoResponse(**data)

@router.post('/new', response_model= BaseResponse, responses= {404:{'model':HTTPError}, 403:{'model':HTTPError}} )
def create_new_user(request: UserRegister):

    data = {
        'name': request.name,
        'username': request.username,
        'password': request.password,
        'email': request.email,
        'phone_number': request.phone_number,
        'role': request.role
    }
    
    
    return BaseResponse(message= 'message test', code= 1200)

@router.put('/info/edit', response_model= BaseResponse, responses= {404:{'model':HTTPError}, 403:{'model':HTTPError}} )
def edit_user_information(request: UserUpdateInfo):

    return BaseResponse(message= 'message test', code= 1200)

@router.put('/pass/edit', response_model= BaseResponse, responses= {404:{'model':HTTPError}, 403:{'model':HTTPError}} )
def change_user_password(request: UserUpdateInfo):

    return BaseResponse(message= 'message test', code= 1200)

@router.put('/role/edit', response_model= BaseResponse, responses= {404:{'model':HTTPError}, 403:{'model':HTTPError}} )
def change_user_role(request: UserUpdateInfo):

    return BaseResponse(message= 'message test', code= 1200)

@router.delete('/delete', response_model= BaseResponse, responses= {404:{'model':HTTPError}, 403:{'model':HTTPError}} )
def delete_user(request: UserUpdateInfo):

    return BaseResponse(message= 'message test', code= 1200)

