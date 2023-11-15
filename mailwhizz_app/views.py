import json
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from mailwhizz_app.helpers import check_if_email_taken
from django.utils.timezone import now as getTimeNow

from mailwhizz_app.langchain import Assistant
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
    
@api_view(['POST'])
@permission_classes([isAuthorized])
def process_email(request):     
    data = json.loads(request.body)    
    try:        
        user_id = data["userId"]                                                                                                                              
        subject = data["subject"]   
        from_email = data["fromEmail"]
        email_body = data["body"]   
        email_body_html = data["htmlBody"]           
        message_id = data["messageId"]            
        attachments = data["attachments"]
        
        try:
            Emails.objects.get(message_id=message_id)            
        except Emails.DoesNotExist:              
            email = Emails(
                message_id=message_id,   
                user_id=user_id,
                subject=subject,
                from_email=from_email,                
                body=email_body_html,                
                created_at=getTimeNow(),
            )
            email.save()

            ai_payload=[
                {"type":"email", "mail":email_body}, 
                {"type":"attachment", "attachments":attachments}
            ]

            tasks = Assistant.extract_tasks_from_email(ai_payload)     
            if len(tasks)>0:
                for item in tasks:                
                    task = Tasks(
                        title=item["task_title"],
                        category=item["task_category"],
                        email_id=email.id,      
                        user_id=user_id,
                        belongs_to=item["belongs_to"],
                        created_at=getTimeNow()
                        )
                    task.save()

            if len(attachments)>0:
                for item in attachments:
                    attachment = Attachments(
                        name=item["fileName"],                        
                        email_id=email.id,      
                        user_id=user_id,                        
                        created_at=getTimeNow()
                        )
                    attachment.save()            

        return Response("Success in processing the email", status=status.HTTP_200_OK)
    except Exception as error:                            
        # Unmuted to see full error !!!!!!!!!
        print("**********************************************************")
        print(traceback.format_exc())           
        print("**********************************************************")                                 
        return Response("An error occured while processing your email", status=status.HTTP_400_BAD_REQUEST)              


@api_view(['GET'])
@permission_classes([isAuthorized])
def fetch_processed_emails(request, user_id):     
    try:
        emails = Emails.objects.filter(user_id=user_id).order_by("-updated_at")      
        serialised_emails = EmailsSerializer(emails, many=True)
        
        tasks = Tasks.objects.filter(user_id=user_id).order_by("-updated_at")
        serialised_tasks = TasksSerializer(tasks, many=True)        

        attachments = Attachments.objects.filter(user_id=user_id).order_by("-updated_at")
        serialised_attachments = AttachmentsSerializer(attachments, many=True)

        results = {
            "emails": serialised_emails.data,
            "tasks": serialised_tasks.data,
            "attachments": serialised_attachments.data
        }                                      
        return Response(results, status=status.HTTP_200_OK)
    except Exception as error:                            
        # Unmuted to see full error !!!!!!!!!
        print("**********************************************************")
        print(traceback.format_exc())           
        print("**********************************************************")                                 
        return Response("An error occured while fetching processed emails", status=status.HTTP_400_BAD_REQUEST)              
    

@api_view(['POST'])
@permission_classes([isAuthorized])
def generate_reply_suggestion(request):   
    data = json.loads(request.body)  
    try:
        text_to_process = ""
        option = ""

        if "attachmentBody" in data:
            text_to_process = data["attachmentBody"]   
            option = "attachment"        
        else: 
            text_to_process = data["emailBody"]         
            option = "email"        

        result = Assistant.generate_reply_suggestion_from_mail(text_to_process, option)        

        return Response(result, status=status.HTTP_200_OK)
    except Exception as error:                            
        # Unmuted to see full error !!!!!!!!!
        print("**********************************************************")
        print(traceback.format_exc())           
        print("**********************************************************")                                 
        return Response("An error occured while generating a reply suggestion", status=status.HTTP_400_BAD_REQUEST)              


@api_view(['POST'])
@permission_classes([isAuthorized])
def generate_mail_summary(request):   
    data = json.loads(request.body)  
    try:
        email_body = data["emailBody"]   

        result = Assistant.generate_summary_from_mail(email_body)

        return Response(result, status=status.HTTP_200_OK)
    except Exception as error:                            
        # Unmuted to see full error !!!!!!!!!
        print("**********************************************************")
        print(traceback.format_exc())           
        print("**********************************************************")                                 
        return Response("An error occured while generating mail summary", status=status.HTTP_400_BAD_REQUEST)              

    