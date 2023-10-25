from django.urls import path
from .views import *

urlpatterns = [
    path('sign_up_user', sign_up_user, name='sign_up_user'),    
    path('sign_in_user', sign_in_user, name='sign_in_user'),        
]
