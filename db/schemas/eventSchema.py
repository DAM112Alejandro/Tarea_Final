def eventSchema(event) -> dict:
    return{
        "id" : str(event["_id"]),
        "title": event["title"],
        "description": event["description"],
        "start_time": str(event["start_time"]),
        "location": event["location"],
        "max_attendees": event["max_attendees"]
    }
    
def eventsSchema(events) -> list:
    return [eventSchema(event) for event in events]