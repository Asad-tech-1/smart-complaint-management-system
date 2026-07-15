from django.utils import timezone
from datetime import timedelta
from .emails import (
    send_status_update_email,
    send_assignment_email,
    send_admin_escalation_email,
)
from accounts.models import User
from .models import Complaint, ComplaintActivity
from .notifications import create_notification

# =========================
# ⏳ SLA SETTINGS
# =========================

SLA_RULES = {
    "critical": timedelta(hours=4),
    "high": timedelta(hours=24),
    "medium": timedelta(hours=48),
    "low": timedelta(hours=72),
}


# =====================================================
# 🔥 Escalate Complaint
# =====================================================

def escalate_complaint(complaint, reason):

    admin = User.objects.filter(role="admin").first()

    old_staff = complaint.assigned_to

    # Save previous owner
    complaint.escalated_from = old_staff

    # Assign Admin
    if admin:
        complaint.assigned_to = admin

    complaint.status = "escalated"
    complaint.is_overdue = True
    complaint.escalation_level += 1
    complaint.save()

    # Activity
    ComplaintActivity.objects.create(
        complaint=complaint,
        event_type="escalated",
        message=reason,
        performed_by=None
    )

    ComplaintActivity.objects.create(
        complaint=complaint,
        event_type="reassigned",
        message="Automatically reassigned to Administrator after SLA breach.",
        performed_by=None
    )

    # Notify previous staff
    if old_staff:

        create_notification(
            old_staff,
            f"Complaint {complaint.tracking_number} exceeded its SLA and has been escalated."
        )
        

    # Notify admin
    if admin:

        create_notification(
            admin,
            f"Complaint {complaint.tracking_number} has been escalated and assigned to you."
        )

    # Notify user

    create_notification(
        complaint.user,
        f"Your complaint ({complaint.tracking_number}) has been escalated for urgent review."
    )
    if admin and admin.email:
     send_admin_escalation_email(complaint)


# =====================================================
# 🔥 MAIN SLA ENGINE
# =====================================================

def run_sla_engine():

    now = timezone.now()

    # ==========================================
    # STEP 1
    # NORMAL SLA BREACH
    # ==========================================

    overdue_complaints = Complaint.objects.filter(
        status__in=["pending", "in_progress"],
        sla_deadline__lt=now
    )

    for complaint in overdue_complaints:

        already_logged = ComplaintActivity.objects.filter(
            complaint=complaint,
            event_type="overdue"
        ).exists()

        if already_logged:
            continue

        ComplaintActivity.objects.create(
            complaint=complaint,
            event_type="overdue",
            message="SLA breached: complaint is overdue.",
            performed_by=None
        )

        escalate_complaint(
            complaint,
            "Complaint automatically escalated after SLA breach."
        )

        print(f"🚨 OVERDUE SLA: Complaint #{complaint.id}")

    # ==========================================
    # STEP 2
    # CRITICAL COMPLAINTS
    # ==========================================

    critical_time = now - timedelta(hours=1)

    critical_complaints = Complaint.objects.filter(
        priority="critical",
        status__in=["pending", "in_progress"],
        created_at__lte=critical_time
    )

    for complaint in critical_complaints:

        already_escalated = ComplaintActivity.objects.filter(
            complaint=complaint,
            event_type="escalated"
        ).exists()

        if already_escalated:
            continue

        escalate_complaint(
            complaint,
            "Critical complaint breached SLA escalation threshold."
        )

        # Extra penalty for critical complaints

        complaint.escalation_level += 1
        complaint.save()

        print(f"🚨 CRITICAL ESCALATION: Complaint #{complaint.id}")