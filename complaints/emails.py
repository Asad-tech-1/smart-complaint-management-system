from datetime import timezone

from django.core.mail import send_mail
from django.conf import settings


def send_complaint_created_email(complaint):

    subject = "Complaint Submitted Successfully"

    message = f"""
    Dear {complaint.user.first_name or complaint.user.username},

    Your complaint has been submitted successfully.

    Complaint Details
    ----------------------------------------

    Tracking Number : {complaint.tracking_number}

    Title           : {complaint.title}

    Department      : {complaint.department}

    Priority        : {complaint.priority.title()}

    Status          : {complaint.status.title()}

    ----------------------------------------

    Our support team will review your complaint as soon as possible.

    Please keep your tracking number for future reference.

    Thank you for using SmartDesk.

    Regards,

    SmartDesk Complaint Management Team
    """

    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [complaint.user.email],
        fail_silently=False,
    )



from django.core.mail import send_mail
from django.conf import settings


def send_assignment_email(complaint):

    subject = "New Complaint Assigned"

    message = f"""
Dear {complaint.assigned_to.first_name or complaint.assigned_to.username},

A new complaint has been assigned to you.

Complaint Details

----------------------------------------

Tracking Number:
{complaint.tracking_number}

Title:
{complaint.title}

Department:
{complaint.department}

Priority:
{complaint.priority.title()}

Submitted By:
{complaint.user.username}

----------------------------------------

Please login to SmartDesk and start working on this complaint.

Regards,

SmartDesk Complaint Management Team
"""

    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [complaint.assigned_to.email],
        fail_silently=False,
    )


from django.core.mail import send_mail
from django.conf import settings


def send_status_update_email(complaint):

    

    from django.utils import timezone

    subject = (
        f"SmartDesk Update {complaint.tracking_number} "
        f"{timezone.now().strftime('%H:%M:%S')}"
    )

    message = f"""
Dear {complaint.user.first_name or complaint.user.username},

Your complaint status has been updated.

Complaint Details
----------------------------

Tracking Number: {complaint.tracking_number}

Title:
{complaint.title}

Current Status:
{complaint.status.replace('_', ' ').title()}

Department:
{complaint.department}

Priority:
{complaint.priority.title()}

If you have any questions, please login to your SmartDesk account to view the latest updates.

Thank you for using SmartDesk Complaint Management System.

Regards,

SmartDesk Support Team
"""

    

    result = send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [complaint.user.email],
        fail_silently=False,
    )

    print("send_mail returned:", result)


from django.core.mail import send_mail
from django.conf import settings


def send_admin_escalation_email(complaint):

    subject = (
        f"Complaint Escalated - {complaint.tracking_number}"
    )

    message = f"""
Dear Administrator,

A complaint has exceeded its SLA deadline and has been automatically escalated.

------------------------------------------------------------

Tracking Number:
{complaint.tracking_number}

Complaint:
{complaint.title}

Submitted By:
{complaint.user.username}

Department:
{complaint.department}

Priority:
{complaint.priority.title()}

Reason:
SLA deadline exceeded.

------------------------------------------------------------

The complaint has now been assigned to you for immediate review.

Please login to the SmartDesk Complaint Management System and take the necessary action as soon as possible.

Regards,

SmartDesk Complaint Management System
"""

    print("ADMIN ESCALATION EMAIL")
    print("Recipient:", complaint.assigned_to.email)

    result = send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [complaint.assigned_to.email],
        fail_silently=False,
    )

    print("send_mail returned:", result)



from django.urls import reverse
from django.core.mail import send_mail
from django.conf import settings


def send_feedback_request_email(complaint):

    print("FEEDBACK EMAIL FUNCTION CALLED")

    feedback_link = (
        f"http://127.0.0.1:8000"
        f"{reverse('submit_feedback', args=[complaint.id])}"
    )

    print("Feedback Link:", feedback_link)

    subject = "We Would Love Your Feedback"

    message = f"""
Hello {complaint.user.username}

Your complaint has been resolved successfully.

Tracking Number:
{complaint.tracking_number}

Complaint:
{complaint.title}

Please rate our service:

{feedback_link}
"""

    print("Recipient:", complaint.user.email)

    result = send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [complaint.user.email],
        fail_silently=False,
    )

    print("send_mail returned:", result)