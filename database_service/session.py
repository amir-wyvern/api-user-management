import grpc 
import grpc_utils.database_pb2_grpc as pb2_grpc
import os

HOST = os.getenv("GRPC_HOST")
PORT = os.getenv("GRPC_PORT")

class GrpcSingleton:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, host, port):
        if not hasattr(self, '_stub'):
            _chanel = grpc.insecure_channel(f'{host}:{port}')
            self._stub = pb2_grpc.DataBaseStub(_chanel)

    @property
    def stub(self):
        return self._stub

session = GrpcSingleton(HOST, PORT)

def get_grpc():
    
    yield session.stub

