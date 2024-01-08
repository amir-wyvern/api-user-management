from grpc_utils.database_pb2_grpc import DataBaseStub
from grpc._channel import _InactiveRpcError
import grpc_utils.database_pb2 as pb2
from typing import Union
from fastapi import (
    HTTPException,
    status
)
from schemas import (
    UserInfoResponse,
    BaseResponse
)
import logging

map_enums = {
    0 : 'ADMIN',
    1 : 'USER'
}

def get_user(caller: str, username: str, stub: DataBaseStub, logger: logging, func: str) -> (Union[dict ,None], Union[HTTPException, None]):

    data = {
        'username': username
    }

    try:

        resp = stub.GetUser(pb2.RequestUserInfo(**data))

    except _InactiveRpcError as InactiveRpcError:
        logger.error(f"[{func}] API-service can't connect to grpc host [caller: {caller} -target_username: {username} -error: {InactiveRpcError}]")
        return None, HTTPException(status_code= status.HTTP_500_INTERNAL_SERVER_ERROR, detail={'code': 2002, 'message': "API-service can't connect to grpc host"})

    except Exception as e:
        logger.error(f'[{func}] Error in grpc connection [caller: {caller} -target_username: {username} -error: {e}]')
        return None, HTTPException(status_code= status.HTTP_500_INTERNAL_SERVER_ERROR, detail={'code': 2003, 'message': "Error in grpc connection"})

    if resp.code == 1401:
        logger.debug(f'[{func}] Username is not found [caller: {caller} -target_username: {username}]')
        return None, HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail={'message': 'Username is not found', 'code': 2401})

    elif resp.code != 1200:
        logger.debug(f'[{func}] error in database service [caller: {caller} -target_username: {username} -err_msg: {resp.message} -err_code: {resp.code}]')
        return None, HTTPException(status_code= status.HTTP_500_INTERNAL_SERVER_ERROR, detail={'message': 'Contact to support!', 'code': resp.code})

    resp_user = {
        'user_id': resp.data.user_id,
        'username': resp.data.username,
        'password': resp.data.password,
        'name': resp.data.name,
        'phone_number': resp.data.phone_number, 
        'role': map_enums[resp.data.role]
    }

    if resp.data.email:
        resp_user.update({'email': resp.data.email})

    return resp_user, None


def create_user(caller: str, data_new_user: dict, stub: DataBaseStub, logger: logging) -> (Union[dict ,None], Union[HTTPException, None]):
    
    try:

        resp = stub.NewUser(pb2.RequestNewUser(**data_new_user)) 

    except _InactiveRpcError as InactiveRpcError:
        logger.error(f"[create user] API-service can't connect to grpc host [caller: {caller} -target_username: {data_new_user['username']} -error: {InactiveRpcError}]")
        return None, HTTPException(status_code= status.HTTP_500_INTERNAL_SERVER_ERROR, detail={'code': 2002, 'message': "API-service can't connect to grpc host"})

    except Exception as e :
        logger.error(f'[create user] Error in grpc connection [caller: {caller} -target_username: {data_new_user["username"]} -error: {e}]')
        return None, HTTPException(status_code= status.HTTP_500_INTERNAL_SERVER_ERROR, detail={'code': 2003, 'message': "Error in grpc connection"})

    if resp.code == 1403:
        logger.debug(f'[create user] Username already exists [caller: {caller} -target_username: {data_new_user["username"]}]')
        return None, HTTPException(status_code= status.HTTP_409_CONFLICT, detail={'message': 'Username already exists', 'code': 2403})
    
    if resp.code == 1406:
        logger.debug(f'[create user] Email already exists [caller: {caller} -target_username: {data_new_user["username"]} -email: {data_new_user["email"]}]')
        return None, HTTPException(status_code= status.HTTP_409_CONFLICT, detail={'message': 'Email already exists', 'code': 2406})
    
    if resp.code == 1407:
        logger.debug(f'[create user] PhoneNumber already exists [caller: {caller} -target_username: {data_new_user["username"]} -phone_number: {data_new_user["phone_number"]}]')
        return None, HTTPException(status_code= status.HTTP_409_CONFLICT, detail={'message': 'PhoneNumber already exists', 'code': 2407})

    if resp.code != 1200:
        logger.debug(f'[create user] error in database service [caller: {caller} -target_username: {data_new_user["username"]} -err_msg: {resp.message} -err_code: {resp.code}]')
        return None, HTTPException(status_code= status.HTTP_500_INTERNAL_SERVER_ERROR, detail={'message': 'Contact to support!', 'code': resp.code})

    return {'message': 'user successfully created', 'code': 1200}, None


def edit_user_info(caller: str, new_user_data: dict, stub: DataBaseStub, logger: logging) -> (Union[dict ,None], Union[HTTPException, None]):

    try:

        resp = stub.ModifyUserInfo(pb2.RequestModifyUserInfo(**new_user_data))

    except _InactiveRpcError as InactiveRpcError:
        logger.error(f"[edit info] API-service can't connect to grpc host [caller: {caller} -error: {InactiveRpcError}]")
        raise HTTPException(status_code= status.HTTP_500_INTERNAL_SERVER_ERROR, detail={'code': 2002, 'message': "API-service can't connect to grpc host"})

    except Exception as e :
        logger.error(f'[edit info] Error in grpc connection [caller: {caller} -error: {e}]')
        raise HTTPException(status_code= status.HTTP_500_INTERNAL_SERVER_ERROR, detail={'code': 2003, 'message': "Error in grpc connection"})

    if resp.code == 1401:
        logger.debug(f'[edit info] Username is not found [caller: {caller}]')
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail={'message': 'Username is not found', 'code': 2401})
    
    if resp.code == 1406:
        logger.debug(f'[create user] Email already exists [caller: {caller} -target_username: {new_user_data["username"]} -email: {new_user_data["email"]}]')
        return None, HTTPException(status_code= status.HTTP_409_CONFLICT, detail={'message': 'Email already exists', 'code': 2406})
    
    if resp.code == 1407:
        logger.debug(f'[create user] PhoneNumber already exists [caller: {caller} -target_username: {new_user_data["username"]} -phone_number: {new_user_data["phone_number"]}]')
        return None, HTTPException(status_code= status.HTTP_409_CONFLICT, detail={'message': 'PhoneNumber already exists', 'code': 2407})

    if resp.code != 1200:
        logger.debug(f'[edit info] error in database service [caller: {caller} -err_msg: {resp.message} -err_code: {resp.code}]')
        raise HTTPException(status_code= status.HTTP_500_INTERNAL_SERVER_ERROR, detail={'message': 'Contact to support!', 'code': resp.code})

    return {'message': 'user information updated successfully', 'code': 1200}, None


def edit_user_password(caller: str, new_password: dict, stub: DataBaseStub, logger: logging) -> (Union[dict ,None], Union[HTTPException, None]):

    try:

        resp = stub.ModifyUserPassword(pb2.RequestModifyUserPassword(**new_password))

    except _InactiveRpcError as InactiveRpcError:
        logger.error(f"[edit pass] API-service can't connect to grpc host [caller: {caller} -error: {InactiveRpcError}]")
        raise HTTPException(status_code= status.HTTP_500_INTERNAL_SERVER_ERROR, detail={'code': 2002, 'message': "API-service can't connect to grpc host"})

    except Exception as e :
        logger.error(f'[edit pass] Error in grpc connection [caller: {caller} -error: {e}]')
        raise HTTPException(status_code= status.HTTP_500_INTERNAL_SERVER_ERROR, detail={'code': 2003, 'message': "Error in grpc connection"})

    if resp.code == 1401:
        logger.debug(f'[edit pass] Username is not found [caller: {caller}]')
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail={'message': 'Username is not found', 'code': 2401})

    if resp.code != 1200:
        logger.debug(f'[edit pass] error in database service [caller: {caller} -err_msg: {resp.message} -err_code: {resp.code}]')
        raise HTTPException(status_code= status.HTTP_500_INTERNAL_SERVER_ERROR, detail={'message': 'Contact to support!', 'code': resp.code})

    return {'message': 'password changed successfully', 'code': 1200}, None


def edit_user_role(caller: str, new_role: dict, stub: DataBaseStub, logger: logging) -> (Union[dict ,None], Union[HTTPException, None]):

    try:

        resp = stub.ModifyUserRole(pb2.RequestModifyUserRole(**new_role))
    
    except _InactiveRpcError as InactiveRpcError:
        logger.error(f"[edit role] API-service can't connect to grpc host [caller: {caller} -target_date: {new_role} -error: {InactiveRpcError}]")
        raise HTTPException(status_code= status.HTTP_500_INTERNAL_SERVER_ERROR, detail={'code': 2002, 'message': "API-service can't connect to grpc host"})

    except Exception as e :
        logger.error(f'[edit role] Error in grpc connection [caller: {caller} -target_data: {new_role} -error: {e}]')
        raise HTTPException(status_code= status.HTTP_500_INTERNAL_SERVER_ERROR, detail={'code': 2003, 'message': "Error in grpc connection"})

    if resp.code == 1401:
        logger.debug(f'[edit role] Username is not found [caller: {caller} -target_data: {new_role}]')
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail={'message': 'Username is not found', 'code': 2401})

    if resp.code != 1200:
        logger.debug(f'[edit role] error in database service [caller: {caller} -target_data: {new_role} -err_msg: {resp.message} -err_code: {resp.code}]')
        raise HTTPException(status_code= status.HTTP_500_INTERNAL_SERVER_ERROR, detail={'message': 'Contact to support!', 'code': resp.code})

    return {'message': 'role updated successfully', 'code': 1200}, None


def delete_user_target(caller: str, delete_username: dict, stub: DataBaseStub, logger: logging) -> (Union[dict ,None], Union[HTTPException, None]):

    try:

        resp = stub.DeleteUser(pb2.RequestDeleteUser(**delete_username))

    except _InactiveRpcError as InactiveRpcError:
        logger.error(f"[delete] API-service can't connect to grpc host [caller: {caller} -target_username: {delete_username['username']} -error: {InactiveRpcError}]")
        raise HTTPException(status_code= status.HTTP_500_INTERNAL_SERVER_ERROR, detail={'code': 2002, 'message': "API-service can't connect to grpc host"})

    except Exception as e :
        logger.error(f'[delete] Error in grpc connection [caller: {caller} -target_username: {delete_username["username"]} -error: {e}]')
        raise HTTPException(status_code= status.HTTP_500_INTERNAL_SERVER_ERROR, detail={'code': 2003, 'message': "Error in grpc connection"})

    if resp.code == 1401:
        logger.debug(f'[delete] Username is not found [caller: {caller} -target_username: {delete_username["username"]}]')
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail={'message': 'Username is not found', 'code': 2401})

    if resp.code != 1200:
        logger.debug(f'[delete] error in database service [caller: {caller} -target_username: {delete_username["username"]} -err_msg: {resp.message} -err_code: {resp.code}]')
        raise HTTPException(status_code= status.HTTP_500_INTERNAL_SERVER_ERROR, detail={'message': 'Contact to support!', 'code': resp.code})

    return {'message': 'user deleted successfully', 'code': 1200}, None
 