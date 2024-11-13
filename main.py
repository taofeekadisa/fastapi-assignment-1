from fastapi import Body, FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from typing import Annotated
from data import users
import uuid
import datetime
import time

app =FastAPI()

class BaseUser(BaseModel):
    first_name:str
    last_name:str
    age:int
    email:EmailStr
    height:float
    
@app.middleware("http")
async def log_rquests(request:Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration= time.time() - start_time
    tracing_Id = str(uuid.uuid4())
    logging_info = {
        "x-request-id": tracing_Id, "method": request.method,
        "status-code":response.status_code,
        "request-endpoint":str(request.url),
        "duration":duration
    }
    print(logging_info)
    
    return response
    

origins = ["http:localhost:8000"]
methods = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=methods,
    allow_headers=["*"],
)


@app.post("/users", status_code=status.HTTP_201_CREATED)
async def create_user(user:Annotated[BaseUser, Body()]):
    for user_profile in users.values():
        if user_profile["email"] == user.email:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,  detail="Email already exists")
    user_Id = str(uuid.uuid4())
    users[user_Id] = user.model_dump()
        #time.sleep(3)
    return {"message": "Profile Created Successfully",
            "data":user.model_dump()}
            
@app.get("/users", status_code=status.HTTP_200_OK)
def get_users():
    return users