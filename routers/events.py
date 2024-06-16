from fastapi import APIRouter, Depends , status , HTTPException
from bson import ObjectId
from db.models.events import Events
from db.schemas.eventSchema import eventSchema , eventSchema, eventsSchema 
from db.client import db
from auth.auth import getToken
from services.mailSender import sendEmail

router = APIRouter(
    prefix="/events",
    tags=["events"],
    responses={status.HTTP_404_NOT_FOUND: {"description": "Not found"}},
)

@router.get("")
async def get_events():
    return eventsSchema(db.events.find())

@router.get("/{id}")
async def get_events_by_id(id):
    return eventSchema(db.events.find_one({"_id": ObjectId(id)}))

@router.post("/add" , response_model=Events)
async def create_event(newEvent: Events, token = Depends(getToken)):
    if db.events.find_one({"title": newEvent.title , 'location': newEvent.location , 'star_time' : newEvent.start_time}):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT , detail="Event already exists")
    
    event_dict = dict(newEvent)
    id = db.events.insert_one(event_dict).inserted_id
    return eventSchema(db.events.find_one({"_id": ObjectId(id)}))

@router.put("/update/{id}" , response_model=Events)
async def update_event(updateEvent: Events ,id : str, token = Depends(getToken)):
    update_data = {
        k: v for k, v in updateEvent.model_dump(exclude_unset=True).items()
        if v not in [None ,  ""  , "string" , 0]  
    }
    
    try:
        db.events.update_one({"_id": ObjectId(id)}, {"$set":update_data })
    except:
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event does not exist")
    
    return eventSchema(db.events.find_one({"_id": ObjectId(id)}))

@router.delete("/delete/{id}")
async def delete_event(id, token = Depends(getToken)):
    found = db.events.find_one({"_id": ObjectId(id)}) 
    if not found:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event does not exist")
    
@router.post("/registerToEvent/{event_id}")
async def register_to_event(event_id , token = Depends(getToken)):
    user = db.users.find_one({"_id": ObjectId(token["_id"])})
    event = db.events.find_one({"_id": ObjectId(event_id)})
    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event does not exist")
    
    if db.registration.count_documents({"event_id": ObjectId(event_id)}) >= event["max_attendees"]:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Event is full")
    
    if db.registration.count_documents({"event_id": ObjectId(event_id), "user_id": ObjectId(user["_id"])}) > 0:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="You are already registered to this event")
    
    sendEmail(user["email"], "Registration to " + event["title"], "You are registered to this event "+event["title"])
    db.registration.insert_one({"event_id": ObjectId(event_id), "user_id": ObjectId(user["_id"])})
    
    
    return {"message": "You are registered to this event "+event["title"]}

@router.delete("/cancelRegistration/{event_id}")
async def cancel_registration(event_id , token = Depends(getToken)):   
    user = db.users.find_one({"_id": ObjectId(token["_id"])})
    event = db.events.find_one({"_id": ObjectId(event_id)})
    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event does not exist")
    
    if not db.registration.find({"event_id": ObjectId(event_id), "user_id": ObjectId(user["_id"])}):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="You are not registered to this event")
    
    sendEmail(user["email"], "Cancelation to " + event["title"], "You cancel your registration to this event " +event["title"])
    db.registration.delete_one({"event_id": ObjectId(event_id), "user_id": ObjectId(user["_id"])})
    
    
    return {"message": "You cancel your registration to this event " +event["title"]}
    
    


    
    
