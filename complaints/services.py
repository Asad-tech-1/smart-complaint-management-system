from accounts.models import User
from .models import ComplaintActivity


# =========================
# 👨‍💼 STAFF ASSIGNMENT
# =========================
def get_assigned_staff(department):

    staff_qs = User.objects.filter(
        role='staff',
        department=department
    )

    if staff_qs.exists():
        return staff_qs.order_by('?').first()

    return User.objects.filter(role='staff').first()


# =========================
# 🧠 ACTIVITY LOGGER (NEW)
# =========================
def log_activity(complaint, event_type, message, user=None):

    return ComplaintActivity.objects.create(
        complaint=complaint,
        event_type=event_type,
        message=message,
        performed_by=user
    )