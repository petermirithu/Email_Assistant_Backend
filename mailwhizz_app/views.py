import json
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from mailwhizz_app.helpers import check_if_email_taken
from django.utils.timezone import now as getTimeNow
from .permissions import isAuthorized
from mailwhizz_app.enc_decryption import check_password, encode_value, hash_password
from mailwhizz_app.models import *
from mailwhizz_app.serializers import *
import traceback

# Create your views here.
@api_view(['POST'])
@permission_classes([])
def sign_up_user(request):
    data = json.loads(request.body)
    try:             
        first_name = data['firstName']                  
        last_name = data['lastName']
        email = data['email']
        password = data['password']         

        taken=check_if_email_taken(email)
        
        if taken==True:            
            return Response('emailTaken', status=status.HTTP_423_LOCKED)
        else:                        
                            
            hashed_password = hash_password(password)                
            new_user = Users(
                        first_name=first_name,
                        last_name=last_name,
                        email=email,   
                        email_provider="gmail",
                        password=str(hashed_password),                            
                        created_at=getTimeNow()
                        )
            new_user.save()
            now = getTimeNow()   
            serialised_user = UsersSerializer(new_user, many=False)                                                                 
            payload = {'id': serialised_user.data["id"],'loggedinAt': now.strftime("%m/%d/%Y, %H:%M:%S")}                    
            new_user.auth_token=encode_value(payload)                                                             
            serialised_user = UsersSerializer(new_user, many=False)                                        
            return Response(serialised_user.data, status=status.HTTP_201_CREATED)
    except:    
        # Unmuted to see full error !!!!!!!!!
        print("**********************************************************")
        print(traceback.format_exc())           
        print("**********************************************************")     
        return Response("Error occured while creating an account", status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['POST'])
def sign_in_user(request):
    data = json.loads(request.body)
    try:
        email = data['email']
        password = data['password']                
        try:
            user = Users.objects.get(email=email)                           

            if(check_password(password, user.password) == True):                    
                now = getTimeNow()   
                serialised_user = UsersSerializer(user, many=False)                                                                 
                payload = {'id': serialised_user.data["id"],'loggedinAt': now.strftime("%m/%d/%Y, %H:%M:%S")}                    
                user.auth_token=encode_value(payload)                                                             
                serialised_user = UsersSerializer(user, many=False)                                        
                return Response(serialised_user.data, status=status.HTTP_200_OK)
            else:
                print("**********************************************************")
                print("Wrong password")           
                print("**********************************************************")     
                return Response("invalidCredentials", status=status.HTTP_400_BAD_REQUEST)                                        
        except Users.DoesNotExist:   
            print("**********************************************************")
            print("User not found")           
            print("**********************************************************")     
            return Response("invalidCredentials", status=status.HTTP_400_BAD_REQUEST)                                                    
    except:
        # Unmuted to see full error !!!!!!!!!
        print("**********************************************************")
        print(traceback.format_exc())           
        print("**********************************************************")     
        return Response("An error occured while authenticating you", status=status.HTTP_400_BAD_REQUEST)                    