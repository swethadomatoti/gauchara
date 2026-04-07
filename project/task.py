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


 

def send_donation_submission_email(name=None, email=None, whatsapp_number=None, amount=None):

    try:
        subject = "New Donation Submitted - Pending Approval"

        # ✅ Correct Quick Pay detection (based on amount)
        is_quick_pay = not amount or amount == 0

        # ✅ Display logic
        display_amount = "Quick Pay" if is_quick_pay else f"₹{amount}"

        # =========================
        # 🟠 QUICK PAY TEMPLATE
        # =========================
        if is_quick_pay:

            html_content = f"""
            <div style="font-family: Arial; max-width: 650px; margin: auto; background:#f9f9f9; padding:20px; border-radius:8px;">
                
                <h2 style="color:#e67e22;">Quick Pay Donation Received</h2>

                <div style="background:#fff; padding:20px; border-radius:6px;">
                    <p><strong>Donor Name:</strong> Unknown</p>
                    <p><strong>Email:</strong> Not Provided</p>
                    <p><strong>WhatsApp:</strong> Not Provided</p>

                    <p>
                        <strong>Donation Amount:</strong> 
                        <span style="color:#27ae60; font-weight:bold;">
                            {display_amount}
                        </span>
                    </p>

                    <p><strong>Payment Type:</strong> Quick Pay</p>

                    <p style="margin-top:15px; color:#555;">
                        User submitted donation using Quick Pay with receipt upload.
                        Please verify the payment from admin panel.
                    </p>
                </div>

                <p style="text-align:center; font-size:12px; color:#aaa;">
                    GAUCHARA Donation System
                </p>
            </div>
            """

        # =========================
        # 🔵 NORMAL TEMPLATE
        # =========================
        else:

            html_content = f"""
            <div style="font-family: Arial; max-width: 650px; margin: auto; background:#f9f9f9; padding:20px; border-radius:8px;">
                
                <h2 style="color:#2c3e50;">New Donation Received</h2>

                <div style="background:#fff; padding:20px; border-radius:6px;">
                    <p><strong>Donor Name:</strong> {name}</p>

                    <p><strong>Email:</strong> 
                        <a href="mailto:{email}" style="color:#3498db;">{email}</a>
                    </p>

                    <p><strong>WhatsApp:</strong> {whatsapp_number}</p>

                    <p>
                        <strong>Donation Amount:</strong> 
                        <span style="color:#27ae60; font-weight:bold;">
                            {display_amount}
                        </span>
                    </p>

                    <p style="margin-top:15px;">
                        This donation is pending approval. Please check admin panel.
                    </p>
                </div>

                <p style="text-align:center; font-size:12px; color:#aaa;">
                    GAUCHARA Donation System
                </p>
            </div>
            """

        # =========================
        # 📤 SEND EMAIL
        # =========================
        mail = Mail(
            from_email=settings.DEFAULT_FROM_EMAIL,
            to_emails=["savadiafoundation@gmail.com"],
            subject=subject,
            html_content=html_content,
        )

        sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
        response = sg.send(mail)

        print("DONATION EMAIL STATUS:", response.status_code)

    except Exception as e:
        print("DONATION EMAIL ERROR:", str(e))

    


def send_donation_email(name, email, whatsapp_number, amount, status):

    print("EMAIL TRIGGERED:", status)

    #  SUCCESS EMAIL
    if status == "success":

        subject = "Donation Successful ❤️"

        user_html = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%); padding: 20px; border-radius: 8px;">
            <div style="background-color: #ffffff; padding: 30px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                <h2 style="color: #27ae60; text-align: center; font-size: 28px; margin: 0 0 10px 0;">Thank You ❤️</h2>
                <p style="text-align: center; color: #7f8c8d; font-size: 14px; margin: 0 0 20px 0;">Your generosity makes a difference</p>
                
                <p style="color: #2c3e50; font-size: 16px; margin: 15px 0;">Dear {name},</p>
                
                <div style="background-color: #f0fdf4; border-left: 4px solid #27ae60; padding: 15px; border-radius: 4px; margin: 20px 0;">
                    <p style="color: #2c3e50; font-size: 14px; line-height: 1.6; margin: 8px 0;">We sincerely thank you for your generous contribution towards GAUCHARA.</p>
                    <p style="color: #2c3e50; font-size: 14px; line-height: 1.6; margin: 8px 0;">Your support helps us provide care, food, and shelter to cows in need.</p>
                </div>
                
                <div style="background-color: #f9f9f9; padding: 15px; border-radius: 4px; margin: 20px 0;">
                    <p style="margin: 10px 0; font-size: 14px;"><strong style="color: #34495e;">WhatsApp:</strong> <span style="color: #2c3e50;">{whatsapp_number}</span></p>
                    <p style="margin: 10px 0; font-size: 14px;"><strong style="color: #34495e;">Email:</strong> <span style="color: #2c3e50;">{email}</span></p>
                    <p style="margin: 10px 0; font-size: 14px;"><strong style="color: #34495e;">Donation Amount:</strong> <span style="color: #27ae60; font-weight: bold; font-size: 16px;">₹{amount}</span></p>
                </div>
                
                <div style="background-color: #e8f8f5; padding: 15px; border-radius: 4px; margin: 20px 0;">
                    <p style="text-align: center; font-size: 14px; color: #16a085; margin: 0; font-weight: bold;">✓ Status: {status.upper()}</p>
                </div>
                
                <p style="text-align: center; color: #34495e; font-size: 16px; margin: 25px 0 10px 0;">🙏 Thank you for supporting Gau Seva</p>
                <p style="text-align: center; color: #95a5a6; font-size: 12px; margin: 20px 0 0 0;">This is an automated message from GAUCHARA.</p>
            </div>
        </div>
        """

    # FAILED EMAIL
    else:

        subject = "Donation Failed ❌"

        user_html = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; background: linear-gradient(135deg, #fef5e7 0%, #f9e79f 100%); padding: 20px; border-radius: 8px;">
            <div style="background-color: #ffffff; padding: 30px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                <h2 style="color: #e74c3c; text-align: center; font-size: 28px; margin: 0 0 10px 0;">Donation Failed ❌</h2>
                <p style="text-align: center; color: #7f8c8d; font-size: 14px; margin: 0 0 20px 0;">We need your assistance</p>
                
                <p style="color: #2c3e50; font-size: 16px; margin: 15px 0;">Dear {name},</p>
                
                <div style="background-color: #ffe6e6; border-left: 4px solid #e74c3c; padding: 15px; border-radius: 4px; margin: 20px 0;">
                    <p style="color: #2c3e50; font-size: 14px; line-height: 1.6; margin: 8px 0;">We regret to inform you that your donation could not be processed successfully.</p>
                    <p style="color: #2c3e50; font-size: 14px; line-height: 1.6; margin: 8px 0;">This may be due to a payment issue or network interruption.</p>
                </div>
                
                <div style="background-color: #f9f9f9; padding: 15px; border-radius: 4px; margin: 20px 0;">
                    <p style="margin: 10px 0; font-size: 14px;"><strong style="color: #34495e;">WhatsApp:</strong> <span style="color: #2c3e50;">{whatsapp_number}</span></p>
                    <p style="margin: 10px 0; font-size: 14px;"><strong style="color: #34495e;">Email:</strong> <span style="color: #2c3e50;">{email}</span></p>
                    <p style="margin: 10px 0; font-size: 14px;"><strong style="color: #34495e;">Attempted Amount:</strong> <span style="color: #e74c3c; font-weight: bold; font-size: 16px;">₹{amount}</span></p>
                </div>
                
                <div style="background-color: #fadbd8; padding: 15px; border-radius: 4px; margin: 20px 0;">
                    <p style="text-align: center; font-size: 14px; color: #c0392b; margin: 0 0 10px 0; font-weight: bold;">✗ Status: {status.upper()}</p>
                    <p style="text-align: center; font-size: 14px; color: #2c3e50; margin: 0;">Please try again or contact us for assistance.</p>
                </div>
                
                <p style="text-align: center; color: #34495e; font-size: 16px; margin: 25px 0 0 0;">We're here to help if you need any support.</p>
                <p style="text-align: center; color: #95a5a6; font-size: 12px; margin: 20px 0 0 0;">This is an automated message from GAUCHARA.</p>
            </div>
        </div>
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
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; background-color: #f9f9f9; padding: 20px; border-radius: 8px;">
        <h2 style="color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 10px; margin-bottom: 20px;">Donation Update - {status.upper()}</h2>
        
        <div style="background-color: #ffffff; padding: 20px; border-radius: 6px;">
            <p style="margin: 12px 0; font-size: 14px;">
                <strong style="color: #34495e;">Status:</strong>
                <span style="background-color: {'#27ae60' if status == 'success' else '#e74c3c'}; color: white; padding: 4px 8px; border-radius: 4px; font-weight: bold;">{status.upper()}</span>
            </p>
            
            <p style="margin: 12px 0; font-size: 14px;">
                <strong style="color: #34495e;">Donor Name:</strong>
                <span style="color: #2c3e50;">{name}</span>
            </p>
            
            <p style="margin: 12px 0; font-size: 14px;">
                <strong style="color: #34495e;">Email:</strong>
                <span style="color: #2c3e50;"><a href="mailto:{email}" style="color: #3498db; text-decoration: none;">{email}</a></span>
            </p>
            
            <p style="margin: 12px 0; font-size: 14px;">
                <strong style="color: #34495e;">WhatsApp:</strong>
                <span style="color: #2c3e50;">{whatsapp_number}</span>
            </p>
            
            <div style="margin-top: 20px; padding-top: 15px; border-top: 1px solid #ecf0f1;">
                <strong style="color: #34495e; display: block; margin-bottom: 8px;">Donation Amount:</strong>
                <p style="color: #27ae60; font-size: 18px; font-weight: bold; margin: 0;">₹{amount}</p>
            </div>
        </div>
        
        <p style="color: #95a5a6; font-size: 12px; margin-top: 20px; text-align: center;">Admin notification from GAUCHARA donation system.</p>
    </div>
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
    <div style="font-family: Arial, sans-serif; max-width: 700px; margin: 0 auto; background-color: #f9f9f9; padding: 20px; border-radius: 8px;">
        <h2 style="color: #2c3e50; border-bottom: 3px solid #9b59b6; padding-bottom: 10px; margin-bottom: 20px;">New Volunteer Registration</h2>
        
        <div style="background-color: #ffffff; padding: 20px; border-radius: 6px;">
            <p style="margin: 12px 0; font-size: 14px;">
                <strong style="color: #34495e;">Full Name:</strong>
                <span style="color: #2c3e50;">{full_name}</span>
            </p>
            
            <p style="margin: 12px 0; font-size: 14px;">
                <strong style="color: #34495e;">Age:</strong>
                <span style="color: #2c3e50;">{age}</span>
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
                <strong style="color: #34495e;">Address:</strong>
                <span style="color: #2c3e50;">{address}</span>
            </p>
            
            <p style="margin: 12px 0; font-size: 14px;">
                <strong style="color: #34495e;">Occupation:</strong>
                <span style="color: #2c3e50;">{occupation}</span>
            </p>
            
            <p style="margin: 12px 0; font-size: 14px;">
                <strong style="color: #34495e;">Availability:</strong>
                <span style="color: #2c3e50;">{availability}</span>
            </p>
            
            <p style="margin: 12px 0; font-size: 14px;">
                <strong style="color: #34495e;">Skills:</strong>
                <span style="color: #2c3e50;">{skills}</span>
            </p>
            
            <div style="margin-top: 20px; padding-top: 15px; border-top: 1px solid #ecf0f1;">
                <strong style="color: #34495e; display: block; margin-bottom: 8px;">Reason for Volunteering:</strong>
                <p style="color: #2c3e50; line-height: 1.6; font-size: 14px; margin: 0; white-space: pre-wrap;">{reason}</p>
            </div>
        </div>
        
        <p style="color: #95a5a6; font-size: 12px; margin-top: 20px; text-align: center;">New volunteer application from GAUCHARA platform.</p>
    </div>
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