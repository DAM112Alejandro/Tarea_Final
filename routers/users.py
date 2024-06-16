from fastapi import APIRouter, Depends , status , HTTPException
from bson import ObjectId
from auth.auth import getToken ,hashPassword 
from db.models.users import Users
from db.client import db
from db.schemas.userSchema import userSchema

router = APIRouter( prefix="/users", tags=["users"] , responses= { status.HTTP_404_NOT_FOUND: {"description": "Not found"}})


@router.put("/update" , response_model=Users)
async def update_event(updateUser: Users , token = Depends(getToken)):
    
    user = db.users.find_one({"_id": ObjectId(token["_id"])})
    
    update_data = {
        k: v for k, v in updateUser.model_dump(exclude_unset=True).items()
        if v not in [None ,  ""  , "string" , 0]  
    }
    
    try:
        if update_data.__contains__('password'):
            update_data['password'] = hashPassword(update_data['password'])
        db.users.update_one({"_id": ObjectId(user["_id"])}, {"$set":update_data })
    except:
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User does not exist")
    
    return userSchema(db.users.find_one({"_id": ObjectId(user["_id"])}))

@router.delete("/delete/{id}")
async def delete_user(id, token = Depends(getToken)):
    found = db.users.find_one({"_id": ObjectId(id)}) 
    if not found:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User does not exist")
