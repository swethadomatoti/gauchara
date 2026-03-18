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

def send_donation_email(name, email, whatsapp_number, amount, payment_id, status):

    print("EMAIL TRIGGERED:", status)

    #  SUCCESS EMAIL
    if status == "success":

        subject = "Donation Successful ❤️"

        user_html = f"""
        <h2>Thank You ❤️</h2>
        <p>Dear {name},</p>
        <p>Whatsapp: {whatsapp_number}</p>
        <p>Email: {email}</p>
        <p>Your donation of ₹{amount} was successful.</p>
        <p>Status: {status}</p>
        <p>Payment ID: {payment_id}</p>
        
        <p>🙏 Thank you for supporting Gau Seva</p>
        """

    # FAILED EMAIL
    else:

        subject = "Donation Failed ❌"

        user_html = f"""
        <h2>Donation Failed</h2>
        <p>Dear {name},</p>
        <p>Whatsapp: {whatsapp_number}</p>
        <p>Email: {email}</p>
        <p>Status: {status}</p>
        <p>Your donation of ₹{amount} has failed.</p>
        <p>Payment ID: {payment_id}</p>
        <p>Please try again.</p>
        """

    # USER EMAIL
    user_mail = Mail(
        from_email=settings.DEFAULT_FROM_EMAIL,
        to_emails=[email],
        subject=subject,
        html_content=user_html
    )

    # ADMIN EMAIL (same for both)
    admin_html = f"""
    <h2>Donation Update</h2>
    <p>Status: {status}</p>
    <p>Name: {name}</p>
    <p>Email: {email}</p>
    <p>WhatsApp: {whatsapp_number}</p>
    <p>Amount: ₹{amount}</p>
    <p>Payment ID: {payment_id}</p>
    """

    admin_mail = Mail(
        from_email=settings.DEFAULT_FROM_EMAIL,
        to_emails=["swethadomatoti3@gmail.com"],
        subject=f"Donation {status.capitalize()}",
        html_content=admin_html
    )

    sg = SendGridAPIClient(settings.SENDGRID_API_KEY)

    sg.send(user_mail)
    sg.send(admin_mail)