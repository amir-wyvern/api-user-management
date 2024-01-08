FROM python:3.9

# Set the working directory in the container
WORKDIR /usr/src/app

# Copy the local code to the container
COPY main.py .
Copy requirements.txt .
COPY schemas.py .
COPY requirements.txt ./requirements.txt

COPY auth/ ./auth
COPY database_service/ ./database_service
COPY cache/ ./cache
COPY router/ ./router
COPY grpc_utils/ ./grpc_utils

RUN pip install --upgrade -r requirements.txt

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]
