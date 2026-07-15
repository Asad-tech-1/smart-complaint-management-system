from django.shortcuts import render
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta
import json

from complaints.models import Complaint, ComplaintActivity
from accounts.models import User

from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.shortcuts import redirect
from django.db.models.functions import TruncMonth

@login_required
def home(request):
  
    # ==========================
    # FILTERS
    # ==========================
    hide_date = timezone.now() - timedelta(days=2)

    complaints = Complaint.objects.exclude(
        is_hidden_from_admin=True,
        hidden_from_admin_at__lt=hide_date
    ).order_by("-created_at")

    status_filter = request.GET.get("status")
    department_filter = request.GET.get("department")
    priority_filter = request.GET.get("priority")

    if status_filter:
        complaints = complaints.filter(status=status_filter)

    if department_filter:
        complaints = complaints.filter(department=department_filter)

    if priority_filter:
        complaints = complaints.filter(priority=priority_filter)

    # ==========================
    # MAIN COUNTS
    # ==========================

    total = complaints.count()

    pending = complaints.filter(status="pending").count()

    in_progress = complaints.filter(status="in_progress").count()

    resolved = complaints.filter(status="resolved").count()
    

    total_staff = User.objects.filter(
        role="staff"
    ).count()

    # ==========================
    # DEPARTMENT BREAKDOWN
    # ==========================

    department_stats = complaints.values(
        "department"
    ).annotate(
        total=Count("id")
    ).order_by("department")

    # ==========================
    # PRIORITY BREAKDOWN
    # ==========================

    priority_stats = complaints.values(
        "priority"
    ).annotate(
        total=Count("id")
    )

    # ==========================
    # CHART DATA
    # ==========================

    dept_labels = []
    dept_values = []

    for item in department_stats:
        dept_labels.append(item["department"])
        dept_values.append(item["total"])

    priority_labels = []
    priority_values = []

    for item in priority_stats:
        priority_labels.append(item["priority"])
        priority_values.append(item["total"])

    # ==========================
    # RECENT COMPLAINTS
    # ==========================

    recent_complaints = complaints.select_related(
        "user",
        "assigned_to"
    )[:5]
    # ==========================
    # STAFF WORKLOAD
    # ==========================

    staff_workload = User.objects.filter(
        role="staff"
    ).annotate(
        total=Count("assigned_complaints")
    ).order_by("-total")

    # ==========================
    # RECENT ACTIVITIES
    # ==========================

    recent_activity = ComplaintActivity.objects.select_related(
        "complaint",
        "performed_by"
    ).order_by("-created_at")[:8]
    


    # ==========================
    # SLA OVERDUE
    # ==========================

    overdue_complaints = Complaint.objects.filter(
        status__in=["pending", "in_progress"],
        sla_deadline__lt=timezone.now()
    )

    overdue_count = overdue_complaints.count()

    # ==========================
    # ESCALATIONS
    # ==========================

    escalations = ComplaintActivity.objects.filter(
        event_type="escalated"
    ).select_related(
        "complaint"
    ).order_by("-created_at")[:10]

    # ==========================
    # DASHBOARD
    # ==========================

    context = {

        # Status Cards
        "total": total,
        "pending": pending,
        "in_progress": in_progress,
        "resolved": resolved,
        "total_staff": total_staff,

        # Complaint List
        "filtered_complaints": complaints,

        # Breakdown Tables
        "department_stats": department_stats,
        "priority_stats": priority_stats,

        # Charts
        "dept_labels": json.dumps(dept_labels),
        "dept_values": json.dumps(dept_values),

        "priority_labels": json.dumps(priority_labels),
        "priority_values": json.dumps(priority_values),

        # SLA
        "overdue_count": overdue_count,
        "overdue_complaints": overdue_complaints,
        "escalations": escalations,

        # New Dashboard Sections
        "recent_complaints": recent_complaints,
        "staff_workload": staff_workload,
        "recent_activity": recent_activity,
    }

    return render(
        request,
        "dashboard/home.html",
        context
    )


# ====================================
# COMPLAINT PAGES
# ====================================
@login_required
def all_complaints(request):

    hide_date = timezone.now() - timedelta(days=2)
    complaints = Complaint.objects.exclude(
        is_hidden_from_admin=True,
        hidden_from_admin_at__lt=hide_date
    ).order_by("-created_at")

    return render(
        request,
        "complaints/list.html",
        {
            "complaints": complaints
        }
    )

@login_required
def pending_complaints(request):

    hide_date = timezone.now() - timedelta(days=2)

    complaints = Complaint.objects.exclude(
        is_hidden_from_admin=True,
        hidden_from_admin_at__lt=hide_date
    ).filter(
        status="pending"
    ).order_by("-created_at")

    return render(
        request,
        "complaints/list.html",
        {
            "complaints": complaints
        }
    )

@login_required
def in_progress_complaints(request):

    hide_date = timezone.now() - timedelta(days=2)

    complaints = Complaint.objects.exclude(
        is_hidden_from_admin=True,
        hidden_from_admin_at__lt=hide_date
    ).filter(
        status="in_progress"
    ).order_by("-created_at")

    return render(
        request,
        "complaints/list.html",
        {
            "complaints": complaints
        }
    )

@login_required
def resolved_complaints(request):

    hide_date = timezone.now() - timedelta(days=2)

    complaints = Complaint.objects.exclude(
        is_hidden_from_admin=True,
        hidden_from_admin_at__lt=hide_date
    ).filter(
        status="resolved"
    ).order_by("-created_at")

    return render(
        request,
        "complaints/list.html",
        {
            "complaints": complaints
        }
    )



from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.db.models import Count
from complaints.models import Complaint
import json


@login_required
def analytics(request):

    if request.user.role != "admin":
        return HttpResponseForbidden("Access Denied")

    # ==========================
    # Monthly Complaint Trend
    # ==========================
    
    total_complaints = Complaint.objects.count()

    monthly_data = (
        Complaint.objects
        .annotate(month=TruncMonth("created_at"))
        .values("month")
        .annotate(total=Count("id"))
        .order_by("month")
    )

    trend_labels = []
    trend_values = []

    for item in monthly_data:
        trend_labels.append(item["month"].strftime("%b %Y"))
        trend_values.append(item["total"])
    
    
    # ==========================
    # Department Performance
    # ==========================

    department_data = (
        Complaint.objects
        .values("department")
        .annotate(total=Count("id"))
        .order_by("department")
    )

    department_labels = []
    department_values = []

    for item in department_data:
        department_labels.append(item["department"])
        department_values.append(item["total"])

   
    # ==========================
    # Staff Performance
    # ==========================

    staff_data = (
        User.objects.filter(role="staff")
        .annotate(total=Count("assigned_complaints"))
        .order_by("-total")
    )

    staff_labels = []
    staff_values = []

    for staff in staff_data:
        staff_labels.append(staff.username)
        staff_values.append(staff.total)
     

    context = {
        "trend_labels": json.dumps(trend_labels),
        "trend_values": json.dumps(trend_values),
        "total_complaints": total_complaints,
        "department_labels": json.dumps(department_labels),
        "department_values": json.dumps(department_values),
        "staff_labels": json.dumps(staff_labels),
        "staff_values": json.dumps(staff_values),
    }

    return render(
        request,
        "dashboard/analytics.html",
        context
    )