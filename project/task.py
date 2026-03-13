from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings


@shared_task
def send_contact_email(name, email, phone, subject, message):

    email_subject = f"New Contact Form Message: {subject}"   

    email_body = f"""
New message received from contact form.

Name: {name}
Email: {email}
Phone: {phone}

Message:
{message}
"""

    send_mail(
        email_subject,                  
        email_body,                     
        settings.DEFAULT_FROM_EMAIL,    
        ["swethadomatoti3@gmail.com"],         
        fail_silently=False,
    )