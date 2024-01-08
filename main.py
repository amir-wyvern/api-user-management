# from dotenv import load_dotenv

# load_dotenv()

from fastapi import FastAPI
from router import (
    auth,
    user
)


description = """
This is a simple service for managing users that connects to the database service via grpc and includes crud operations on the database. 🚀
## Items

* Create User
* Delete User
* Change Role 
* Edit information 
"""

app = FastAPI(    
    title="User-Management",
    description=description,
    version="0.0.1",
    contact={
        "name": "WyVern",
        "email": "amirhosein_wyvern@yahoo.com"
    },
    license_info={
        "name": "MIT"
    },) 

app.include_router(user.router)
app.include_router(auth.router)
