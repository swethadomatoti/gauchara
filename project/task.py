from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from django.conf import settings

def send_contact_email(name, email, phone, subject, message):
    try:
        html_content = f"""
        <p><strong>Name:</strong> {name}</p>
        <p><strong>Email:</strong> {email}</p>
        <p><strong>Phone:</strong> {phone}</p>
        <p><strong>Subject:</strong> {subject}</p>
        <p><strong>Message:</strong><br>{message}</p>
        """

        mail = Mail(
            from_email=settings.DEFAULT_FROM_EMAIL,
            to_emails="swethadomatoti3@gmail.com",
            subject=f"New Contact Form Message: {subject}",
            html_content=html_content,
        )

        sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
        response = sg.send(mail)

        print("✅ EMAIL STATUS:", response.status_code)
        print("✅ RESPONSE BODY:", response.body)

    except Exception as e:
        print("❌ EMAIL ERROR:", str(e))