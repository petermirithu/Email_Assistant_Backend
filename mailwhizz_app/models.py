from mongoengine import *
import datetime

# Create your models here.
class Users(Document):     
    first_name=StringField(required=True)
    last_name=StringField(required=True)
    email=StringField(required=True)
    email_provider: StringField(required=True)
    password=StringField(required=True)        
    auth_token=StringField()
    created_at=DateTimeField(required=True)
    updated_at=DateTimeField(default=datetime.datetime.utcnow)

    