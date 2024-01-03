from fastapi import (
    APIRouter
)
from schemas import (
    BaseResponse,
    UserRegister,
    HTTPError
)
import grpc
import grpc_utils.database_pb2_grpc as pb2_grpc
import grpc_utils.database_pb2 as pb2

chanel = grpc.insecure_channel('localhost:3333')
stub = pb2_grpc.DataBaseStub(chanel)


router = APIRouter(prefix='/user', tags=['User'])

@router.post('/new', response_model= BaseResponse, responses= {404:{'model':HTTPError}, 403:{'model':HTTPError}} )
def create_new_user(request: UserRegister):
    print(request)

    data = {
        'name': request.name,
        'username': request.username,
        'password': request.password,
        'email': request.email,
        'phone_number': request.phone_number,
        'role': request.role
    }
    x = pb2.RequestNewUSer(**data)
    resp = stub.NewUser(x )
    return BaseResponse(message= resp.message)

