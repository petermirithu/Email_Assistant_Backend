from django.urls import path
from .views import *

urlpatterns = [
    path('sign_up_user', sign_up_user, name='sign_up_user'),    
    path('sign_in_user', sign_in_user, name='sign_in_user'),        
    
    path('process_email', process_email, name='process_email'),                
    path('fetch_processed_emails/<str:user_id>', fetch_processed_emails, name='fetch_processed_emails'),                    
    path('generate_reply_suggestion', generate_reply_suggestion, name='generate_reply_suggestion'),                
    path('generate_mail_summary', generate_mail_summary, name='generate_mail_summary'),                    
]
