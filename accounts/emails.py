from django.core.mail import send_mail
from django.conf import settings

def send_welcome_email(user):

    print("Sending email to:", user.email)

    subject = "Welcome to SmartDesk"

    message = f"""
Hello {user.first_name or user.username},

Welcome to SmartDesk.

Your account has been created successfully.

Username: {user.username}
Email: {user.email}

Thank you for using SmartDesk.

Regards,
SmartDesk Team
"""

    result = send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        fail_silently=False,
    )

    print("Mail sent:", result)