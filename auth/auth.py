from datetime import datetime,timedelta, timezone
from typing import Annotated
from bson import ObjectId
from fastapi import Depends, HTTPException, APIRouter ,status
from pydantic import BaseModel
from passlib.context import CryptContext 
from fastapi.security import HTTPBearer, OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from db.client import db


from db.models.users import Users
from config import SECRET_KEY , ALGORITHM , ACCESS_TOKEN_EXPIRE_MINUTES
router = APIRouter( prefix="/auth", tags=["auth"])

brcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")   
#Solo auth con jwt
#auth =  HTTPBearer()

class CreateUserRequest(BaseModel):
    username: str
    email : str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    
    
@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(user: CreateUserRequest):
    create_user = Users(
        username = user.username,
        email = user.email,
        password =  brcrypt_context.hash(user.password)
    )
    user_dict = create_user.model_dump()
    db.users.insert_one(user_dict)
    return {'message': 'user created successfully'}
    
@router.post("/login")
async def login(form_data: Annotated[OAuth2PasswordRequestForm ,Depends()]):
    user = authenticateUser(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    token = create_token(user['username'], user['_id'] , timedelta(minutes=float(ACCESS_TOKEN_EXPIRE_MINUTES)))
    return {"access_token": token, "token_type": "bearer"}

def authenticateUser(username: str, password: str):
    user = db.users.find_one({"username": username})
    if not user:
        return False
    if not brcrypt_context.verify(password, user["password"]):
        return False
    return user

def create_token(username: str, id: ObjectId, expires_delta: timedelta):
    encode  = { 'sub': username , 'id': str(id) }
    expire = datetime.now(timezone.utc) + expires_delta
    encode.update({"exp": expire})
    return jwt.encode(encode, SECRET_KEY, ALGORITHM)

def getToken(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        id: str = payload.get("id")
        if id is None:
            raise credentials_exception
        token_data = db.users.find_one({"_id": ObjectId(id)})
        if token_data is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    return token_data

def hashPassword(password: str):
    return brcrypt_context.hash(password)


    