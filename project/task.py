from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from django.conf import settings

def send_contact_email(name, email, phone, subject, message):
    try:
        html_content = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; background-color: #f9f9f9; padding: 20px; border-radius: 8px;">
            <h2 style="color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 10px;">New Contact Form Message</h2>
            
            <div style="background-color: #ffffff; padding: 20px; border-radius: 6px; margin-top: 15px;">
                <p style="margin: 12px 0; font-size: 14px;">
                    <strong style="color: #34495e;">Name:</strong>
                    <span style="color: #2c3e50;">{name}</span>
                </p>
                
                <p style="margin: 12px 0; font-size: 14px;">
                    <strong style="color: #34495e;">Email:</strong>
                    <span style="color: #2c3e50;"><a href="mailto:{email}" style="color: #3498db; text-decoration: none;">{email}</a></span>
                </p>
                
                <p style="margin: 12px 0; font-size: 14px;">
                    <strong style="color: #34495e;">Phone:</strong>
                    <span style="color: #2c3e50;">{phone}</span>
                </p>
                
                <p style="margin: 12px 0; font-size: 14px;">
                    <strong style="color: #34495e;">Subject:</strong>
                    <span style="color: #2c3e50;">{subject}</span>
                </p>
                
                <div style="margin-top: 20px; padding-top: 15px; border-top: 1px solid #ecf0f1;">
                    <strong style="color: #34495e; display: block; margin-bottom: 8px;">Message:</strong>
                    <p style="color: #2c3e50; line-height: 1.6; font-size: 14px; white-space: pre-wrap;">{message}</p>
                </div>
            </div>
            
            <p style="color: #95a5a6; font-size: 12px; margin-top: 20px; text-align: center;">This is an automated message from GAUCHARA contact form.</p>
        </div>
        """

        mail = Mail(
            from_email=settings.DEFAULT_FROM_EMAIL,
            to_emails="savadiafoundation@gmail.com",
            subject=f"New Contact Form Message: {subject}",
            html_content=html_content,
        )

        sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
        response = sg.send(mail)

        print("EMAIL STATUS:", response.status_code)
        print("RESPONSE BODY:", response.body)

    except Exception as e:
        print(" EMAIL ERROR:", str(e))

def send_donation_email(name, email, whatsapp_number, amount, status):

    print("EMAIL TRIGGERED:", status)

    #  SUCCESS EMAIL
    if status == "success":

        subject = "Donation Successful ❤️"

        user_html = f"""
        <h2>Thank You ❤️</h2>
        <p>Dear {name},</p>
            <div>
             <p>We sincerely thank you for your generous contribution towards GAUCHARA.</p>
            <p>Your support helps us provide care, food, and shelter etc.. to cows in need.</p>
            </div>
        <p>Whatsapp: {whatsapp_number}</p>
        <p>Email: {email}</p>
        <p>Your donation of ₹{amount} was successful.</p>
        <p>Status: {status}</p>
        
        <p>🙏 Thank you for supporting Gau Seva</p>
        """

    # FAILED EMAIL
    else:

        subject = "Donation Failed ❌"

        user_html = f"""
        <h2>Donation Failed</h2>
        <p>Dear {name},</p>
            <div
            <p>We regret to inform you that your donation could not be processed successfully.</p>
            <p>This may be due to a payment issue or network interruption.</p>
            </div>
        <p>Whatsapp: {whatsapp_number}</p>
        <p>Email: {email}</p>
        <p>Status: {status}</p>
        <p>Your donation of ₹{amount} has failed.</p>
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
    """

    admin_mail = Mail(
        from_email=settings.DEFAULT_FROM_EMAIL,
        to_emails=["savadiafoundation@gmail.com"],
        subject=f"Donation {status.capitalize()}",
        html_content=admin_html
    )

    sg = SendGridAPIClient(settings.SENDGRID_API_KEY)

    sg.send(user_mail)
    sg.send(admin_mail)
    

def send_volunteer_email(full_name, age, email, phone, address,
                         occupation, availability, skills, reason):

    print("VOLUNTEER EMAIL SENT TO ADMIN")

    admin_html = f"""
    <h2>New Volunteer Registration</h2>

    <p><b>Name:</b> {full_name}</p>
    <p><b>Age:</b> {age}</p>
    <p><b>Email:</b> {email}</p>
    <p><b>Phone:</b> {phone}</p>
    <p><b>Address:</b> {address}</p>
    <p><b>Occupation:</b> {occupation}</p>
    <p><b>Availability:</b> {availability}</p>
    <p><b>Skills:</b> {skills}</p>
    <p><b>Reason:</b> {reason}</p>
    """

    message = Mail(
        from_email=settings.DEFAULT_FROM_EMAIL,
        to_emails=["savadiafoundation@gmail.com"],  # ADMIN ONLY
        subject="New Volunteer Application",
        html_content=admin_html
    )

    sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
    response = sg.send(message)

    print("STATUS:", response.status_code) 