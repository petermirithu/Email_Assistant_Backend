from mongoengine import *
import datetime

# Create your models here.
class Users(Document):     
    first_name=StringField(required=True)
    last_name=StringField(required=True)
    email=StringField(required=True)
    email_provider=StringField(required=True)
    password=StringField(required=True)        
    auth_token=StringField()
    created_at=DateTimeField(required=True)
    updated_at=DateTimeField(default=datetime.datetime.utcnow)

class Emails(Document):     
    user_id = ReferenceField(Users, reverse_delete_rule=CASCADE)      
    message_id = StringField(required=True)
    subject=StringField(required=True)
    from_email=StringField(required=True)
    read=BooleanField(default=False)
    body=StringField(required=True)                        
    created_at=DateTimeField(required=True)
    updated_at=DateTimeField(default=datetime.datetime.utcnow)

class Tasks(Document):     
    email_id = ReferenceField(Emails, reverse_delete_rule=CASCADE)      
    title=StringField(required=True)
    category=StringField(required=True)
    done=BooleanField(default=False)
    created_at=DateTimeField(required=True)
    updated_at=DateTimeField(default=datetime.datetime.utcnow)

class Attachments(Document):     
    email_id = ReferenceField(Emails, reverse_delete_rule=CASCADE)      
    name=StringField(required=True)
    key_points=StringField(required=True)            
    read=BooleanField(default=False)    
    created_at=DateTimeField(required=True)
    updated_at=DateTimeField(default=datetime.datetime.utcnow)