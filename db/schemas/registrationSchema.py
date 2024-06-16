def registrationSchema(registration) -> dict:
    return{
        "id_Event": str(registration["event_id"]),
        "id_User": str(registration["user_id"]),
    }
    
def registrationsSchema(registrations) -> list:
    return [registrationSchema(registration) for registration in registrations]