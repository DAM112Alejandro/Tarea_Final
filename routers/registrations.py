from fastapi import APIRouter, Depends , status , HTTPException
from bson import ObjectId
from db.client import db
from auth.auth import getToken
from db.schemas.eventSchema import eventsSchema


router = APIRouter(
    prefix="/registration",
    tags=["registration"],
    responses={status.HTTP_404_NOT_FOUND: {"description": "Not found"}},
)

@router.get("/user")
def getRegistrationByUser(token = Depends(getToken)):
    user = db.users.find_one({"_id": ObjectId(token["_id"])})
    registrations = db.registration.find({"user_id": ObjectId(user["_id"])})
    
    events = []
    
    for registration in registrations:
        event = db.events.find_one({"_id": ObjectId(registration["event_id"])})
        events.append(event)
    
    return eventsSchema(events)
