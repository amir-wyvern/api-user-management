# AUM-gRPC
## _The API-User-Managment_
This program is an api that gives access to creating, editing, deleting and fetching user information in grpc services connected to it

## Features

- Create New User (Admin)
- Edit User Information
- Edit User Password
- Fetch User Data
- ✨ Change User Role (Admin) ✨


This repository is made of 2 separate services
1. Redis service
2. FastAPI Serive






## How It Works
> This service receives requests from the user and sends them to the gDataBase service via gRPC
Also, the caching process is also included in this service in such a way that the caching service is used to store user tokens

> 
> This service is completely dockerized and you need to set environment in it
> But before doing this, you need to create a network manually via docker so that in the
> future you can put all the services you need on an internal network of
> containers.

Create Network via docker:

```sh
docker network create share-net
```

Then set Environments in __docker-compose.yml__ .
| Environments | Value | Description |
| ------ | ------ | ------ |
| OAUTH2_SECRET_KEY | test_09d25e094faa6c | _client secret for create jwt token_ |
| OAUTH2_ALGORITHM | HS256 | _cryptographic algorithm used to hash information in the context of OAuth 2.0 (HMAC-SHA256)_ |
| GRPC_HOST | grpc_service | _grpc service host name in gDataBase service_ |
| GRPC_PORT | 3333 | _grpc service port in gDataBase service_ |
| CACHE_URL | redis://cache_db:6379 | url cache for redis database |

> Note 1: Redis Host is available in docker-compose.yml (**cache_db service**)
> Note 2: GRPC_HOST is available in another project (__gDataBase__) in docker-compose.yml  (**grpc_service service**)

In Finally
```sh
docker compose up
```

Now You can access to FastApi Docs 
```sh
http://localhost:8585/docs
```

## Architecture

![Architecture](https://github.com/amir-wyvern/api-user-management/blob/main/pic.png)

## License

MIT

**Free Software, Hell Yeah!**
