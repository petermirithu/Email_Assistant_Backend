from rest_framework_mongoengine import serializers
from mailwhizz_app.models import *

class UsersSerializer(serializers.DocumentSerializer):
    class Meta:
        model=Users
        exclude=("password",)