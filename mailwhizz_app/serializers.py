from rest_framework_mongoengine import serializers
from mailwhizz_app.models import *

class UsersSerializer(serializers.DocumentSerializer):
    class Meta:
        model=Users
        exclude=("password",)

class EmailsSerializer(serializers.DocumentSerializer):
    class Meta:
        model=Emails
        fields="__all__" 

class TasksSerializer(serializers.DocumentSerializer):
    class Meta:
        model=Tasks
        fields="__all__" 

class AttachmentsSerializer(serializers.DocumentSerializer):
    class Meta:
        model=Attachments
        fields="__all__" 