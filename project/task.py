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

        print("EMAIL STATUS:", response.status_code)
        print("RESPONSE BODY:", response.body)

    except Exception as e:
        print(" EMAIL ERROR:", str(e))

def send_donation_email(name, email, whatsapp_number, amount, payment_id):

    print("EMAIL FUNCTION CALLED")   

    user_html = f"""
    <h2>Thank You ❤️</h2>
    <p>Dear {name},</p>
    <p>Your mail: {email}</p>
    <p>Your whatsapp number: {whatsapp_number}</p>
    <p>Your donation of ₹{amount} is successful.</p>
    <p>Payment ID: {payment_id}</p>
    <br>
    <p>🙏 Thank you for supporting Gau Seva</p>
    """

    user_mail = Mail(
        from_email=settings.DEFAULT_FROM_EMAIL,
        to_emails=[email],   
        subject="Donation Successful",
        html_content=user_html
    )

    admin_mail = Mail(
        from_email=settings.DEFAULT_FROM_EMAIL,
        to_emails=["swethadomatoti3@gmail.com"],   
        subject="New Donation Received",
        html_content=f"New donation from {name} {email} {whatsapp_number} ₹{amount}"
    )

    sg = SendGridAPIClient(settings.SENDGRID_API_KEY)

  
    response1 = sg.send(user_mail)
    print("USER MAIL STATUS:", response1.status_code)

    response2 = sg.send(admin_mail)
    print("ADMIN MAIL STATUS:", response2.status_code)