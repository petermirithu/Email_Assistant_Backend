from .models import Users

def check_if_email_taken(email):
    try:
        found = Users.objects.get(email=email)
        return True
    except Users.DoesNotExist:
        return False    
    