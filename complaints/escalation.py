from django.utils import timezone

from .models import Complaint, ComplaintActivity
from .notifications import create_notification


def check_sla_violations():

    overdue = Complaint.objects.filter(
        status__in=["pending", "in_progress"],
        is_overdue=False,
        sla_deadline__lt=timezone.now()
    )

    for complaint in overdue:

        complaint.is_overdue = True
        complaint.escalation_level += 1
        complaint.status = "escalated"

        complaint.save()

        ComplaintActivity.objects.create(
            complaint=complaint,
            event_type="escalated",
            message="Complaint automatically escalated because SLA expired.",
            performed_by=None,
        )

        create_notification(
            complaint.user,
            f"Your complaint '{complaint.title}' has been escalated."
        )

        if complaint.assigned_to:
            create_notification(
                complaint.assigned_to,
                f"Complaint '{complaint.title}' exceeded SLA."
            )

        print(
            f"Complaint {complaint.tracking_number} escalated."
        )