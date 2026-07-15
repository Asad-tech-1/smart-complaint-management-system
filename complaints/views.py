import json
from urllib import request
from .emails import (
    send_complaint_created_email,
    send_assignment_email,
    send_status_update_email,
    send_feedback_request_email,
)
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Count
from django.contrib.auth import get_user_model
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from .models import Complaint, ComplaintActivity, ComplaintRemark
from .forms import ComplaintForm
from .ai import analyze_complaint
from .notifications import create_notification
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from .forms import ComplaintFeedbackForm
from .models import ComplaintFeedback
from django.contrib import messages

User = get_user_model()


# =========================
# 🔐 SYSTEM USER (FALLBACK)
# =========================

def get_system_user():
    """
    Always returns a valid user so AnonymousUser never breaks DB
    """
    user = User.objects.first()

    if not user:
        user = User.objects.create(
            username="system_user"
        )

    return user



from django.utils import timezone
from datetime import timedelta
# =========================
# 👤 CREATE COMPLAINT
# =========================
from django.utils import timezone
from datetime import timedelta


def create_complaint(request):

    

    if request.method == "POST":

        form = ComplaintForm(request.POST, request.FILES)

        if form.is_valid():

            complaint = form.save(commit=False)

            # 👤 SYSTEM USER
            complaint.user = request.user

            # =========================
            # 🤖 AI ANALYSIS
            # =========================

            text = f"{complaint.title}\n\n{complaint.description}"

            ai_result = analyze_complaint(text)

            print("RAW AI OUTPUT:", ai_result)
            print(ai_result)

            print("RAW AI OUTPUT:", ai_result)

            department = "General"
            priority = "low"

            try:

                data = json.loads(ai_result)

                department = (
                    data.get("department")
                    or "General"
                )

                priority = (
                    data.get("priority")
                    or "low"
                )

            except Exception as e:

                print("AI parsing failed:", e)

            # =========================
            # 🧠 AI OUTPUT
            # =========================

            complaint.department = department
            complaint.priority = priority
            complaint.status = "pending"

            # =========================
            # ⏳ SLA ENGINE
            # =========================

            if priority == "critical":

                complaint.sla_deadline = (
                    timezone.now() +
                    timedelta(hours=4)
                )

            elif priority == "high":

                complaint.sla_deadline = (
                    timezone.now() +
                    timedelta(hours=24)
                )

            elif priority == "medium":

                complaint.sla_deadline = (
                    timezone.now() +
                    timedelta(hours=48)
                )

            else:

                complaint.sla_deadline = (
                    timezone.now() +
                    timedelta(hours=72)
                )

            # =========================
            # 👨‍💼 SMART ASSIGNMENT
            # =========================

            staff_user = get_smart_assigned_staff(
                department
            )

            complaint.assigned_to = (
                staff_user
                or User.objects.filter(
                    is_staff=True
                ).first()
            )

            # =========================
            # 💾 SAVE COMPLAINT
            # =========================

            if complaint.status == "resolved" and not complaint.resolved_at:
                complaint.resolved_at = timezone.now()

            # Save first to get the database ID
            complaint.save()

            # Generate tracking number
            complaint.tracking_number = (
                f"CMP-{timezone.now().year}-{complaint.id:06d}"
            )

            complaint.save(update_fields=["tracking_number"])
            # Send confirmation email to the user
            send_complaint_created_email(complaint)
            if complaint.assigned_to and complaint.assigned_to.email:
                send_assignment_email(complaint)

            # =========================
            # 🧠 EVENT LOGS
            # =========================

            ComplaintActivity.objects.create(
                complaint=complaint,
                event_type="created",
                message="Complaint created",
                performed_by=request.user
            )

            ComplaintActivity.objects.create(
                complaint=complaint,
                event_type="ai_assigned",
                message=f"Department auto-detected as {department}",
                performed_by=request.user
            )

            ComplaintActivity.objects.create(
                complaint=complaint,
                event_type="ai_assigned",
                message=f"Priority auto-detected as {priority}",
                performed_by=request.user
            )

            # =========================
            # ⏳ SLA EVENT
            # =========================

            ComplaintActivity.objects.create(
                complaint=complaint,
                event_type="sla_created",
                message=(
                    f"SLA deadline set to "
                    f"{complaint.sla_deadline.strftime('%d %b %Y %H:%M')}"
                ),
                performed_by=request.user
            )

            # =========================
            # 👨‍💼 ASSIGNMENT EVENT
            # =========================

            if complaint.assigned_to:
                ComplaintActivity.objects.create(
                    complaint=complaint,
                    event_type="assigned",
                    message=(
                        f"Assigned to "
                        f"{complaint.assigned_to.username}"
                    ),
                    performed_by=request.user
                )

                create_notification(
                complaint.assigned_to,
                f"New complaint assigned: {complaint.title}"
            )

            return redirect('my_complaints')

    else:

        form = ComplaintForm()

    return render(
        request,
        'complaints/create.html',
        {
            'form': form
        }
    )


# =========================
# 👤 USER COMPLAINT LIST
# =========================

# =========================
# 👨‍💼 STAFF COMPLAINT LIST
# =========================

@login_required
def staff_complaints(request):

    if request.user.role != "staff":
        return HttpResponseForbidden("Access Denied")

    complaints = Complaint.objects.filter(
        assigned_to=request.user
    ).exclude(
        status__in=["resolved", "rejected"]
    ).order_by("-created_at")

    return render(
        request,
        "complaints/staff_list.html",
        {
            "complaints": complaints
        }
    )


# =========================
# 🧠 STAFF ASSIGNMENT
# =========================
from django.db.models import Count


def get_smart_assigned_staff(department):

    staff_users = User.objects.filter(
        role="staff",
        department=department
    )

    if staff_users.exists():

        return staff_users.annotate(
            load=Count("assigned_complaints")
        ).order_by("load").first()

    # If no staff exists for that department,
    # assign to the least busy staff member.
    return User.objects.filter(
        role="staff"
    ).annotate(
        load=Count("assigned_complaints")
    ).order_by("load").first()


# =========================
# ⚙️ MASTER DETAIL
# =========================
@login_required
def complaint_master_detail(request, pk):

    complaint = get_object_or_404(Complaint, id=pk)

    # ==========================
    # ADMIN ACCESS
    # ==========================
    if request.user.role == "admin":
        is_admin = True

    # ==========================
    # STAFF ACCESS
    # ==========================
    elif request.user.role == "staff":

        # Staff can ONLY open complaints assigned to them
        if complaint.assigned_to != request.user:
            return HttpResponseForbidden("Access Denied")

        is_admin = False

    else:
        return HttpResponseForbidden("Access Denied")

    staff_users = User.objects.filter(role="staff")

    if request.method == "POST":

        old_status = complaint.status
        old_assigned = complaint.assigned_to
        

        # -------------------------
        # STAFF CAN UPDATE
        # -------------------------
        complaint.status = request.POST.get("status")

        # ==========================
        # RESOLVED
        # ==========================

        if complaint.status == "resolved":

            # Staff should never see resolved complaints
            complaint.is_hidden_from_staff = True

            # Admin can still see it for 2 days
            complaint.is_hidden_from_admin = True
            complaint.hidden_from_admin_at = timezone.now()

            complaint.resolved_at = timezone.now()


        # ==========================
        # REJECTED
        # ==========================

        elif complaint.status == "rejected":

            # Staff loses it immediately
            complaint.is_hidden_from_staff = True

            # Admin keeps it for 2 days
            complaint.is_hidden_from_admin = True
            complaint.hidden_from_admin_at = timezone.now()


        # ==========================
        # ESCALATED
        # ==========================

        elif complaint.status == "escalated":

            complaint.escalated_from = complaint.assigned_to
            complaint.assigned_to = request.user
                

        # -------------------------
        # ADMIN ONLY
        # -------------------------
        if is_admin:

            assigned_to_id = request.POST.get("assigned_to")

            if assigned_to_id:
                complaint.assigned_to = User.objects.get(id=assigned_to_id)

            department = request.POST.get("department")
            priority = request.POST.get("priority")

            if department:
                complaint.department = department

            if priority:
                complaint.priority = priority

        complaint.save()
        remark_text = request.POST.get("remarks", "").strip()

        if remark_text:

            ComplaintRemark.objects.create(
                complaint=complaint,
                author=request.user,
                message=remark_text,
                is_public=True
            )

            ComplaintActivity.objects.create(
                complaint=complaint,
                event_type="remarks_added",
                message="Staff added a new update.",
                performed_by=request.user
            )

            create_notification(
                complaint.user,
                f"Your complaint '{complaint.title}' has a new update."
            )

        # -------------------------
        # STATUS EVENT
        # -------------------------
        # -------------------------
        # STATUS EVENT
        # -------------------------
        if old_status != complaint.status:

            print("Status changed!")
            print(old_status, "->", complaint.status)

            # ==========================
            # SEND STATUS EMAIL
            # ==========================
            if complaint.status in ["in_progress", "resolved", "rejected"]:

                print("Sending status email...")
                try:
                    send_status_update_email(complaint)
                except Exception as e:
                    print("Email Error:", e)

            # ==========================
            # SEND FEEDBACK EMAIL
            # ==========================
            if complaint.status == "resolved":

                print("Sending feedback email...")
                try:
                    send_feedback_request_email(complaint)
                except Exception as e:
                    print("Email Error:", e)

            # ==========================
            # Activity Type
            # ==========================
            if complaint.status == "resolved":
                event = "resolved"

            elif complaint.status == "rejected":
                event = "rejected"

            elif complaint.status == "escalated":
                event = "escalated"

            else:
                event = "status_changed"

            ComplaintActivity.objects.create(
                complaint=complaint,
                event_type=event,
                message=f"{old_status} → {complaint.status}",
                performed_by=request.user
            )

            create_notification(
                complaint.user,
                f"Complaint '{complaint.title}' status changed to {complaint.status}"
            )

        # -------------------------
        # REASSIGN EVENT
        # -------------------------
        if is_admin and old_assigned != complaint.assigned_to:

            ComplaintActivity.objects.create(
                complaint=complaint,
                event_type="reassigned",
                message=f"Reassigned to {complaint.assigned_to.username}",
                performed_by=request.user
            )

            create_notification(
                complaint.assigned_to,
                f"Complaint '{complaint.title}' has been assigned to you"
            )

        
        if complaint.status == "rejected":

            ComplaintActivity.objects.create(
                complaint=complaint,
                event_type="rejected",
                message="Complaint rejected by administrator.",
                performed_by=request.user
            )

            create_notification(
                complaint.user,
                f"Your complaint '{complaint.title}' has been rejected."
            )

        return redirect("complaint_master_detail", pk=pk)
    
    assigned_staff = complaint.assigned_to

    staff_workload = 0

    if assigned_staff:
        staff_workload = Complaint.objects.filter(
            assigned_to=assigned_staff,
            status__in=["pending", "in_progress", "escalated"]
        ).count()

    context = {
        "complaint": complaint,
        "staff_users": staff_users,
        "assigned_staff": assigned_staff,
        "staff_workload": staff_workload,
        "is_admin": is_admin,
        "remarks": ComplaintRemark.objects.filter(
            complaint=complaint
        )
    }

    if is_admin:
        return render(
            request,
            "complaints/master_detail.html",
            context
        )

    return render(
        request,
        "complaints/staff/complaint_workspace.html",
        context
    )

from .models import Notification

@login_required
def notification_list(request):

    notifications = Notification.objects.filter(
        user=request.user
    ).order_by("-created_at")

    if request.user.role == "user":
        base_template = "user/base_user.html"
    elif request.user.role == "staff":
        base_template = "staff/base_staff.html"
    else:
        base_template = "base.html"   # Admin

    return render(
        request,
        "complaints/notifications.html",
        {
            "notifications": notifications,
            "base_template": base_template,
        }
    )


    from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import Complaint


from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import Complaint

@login_required
def user_dashboard(request):

    if request.user.role != "user":
        return HttpResponseForbidden("Access Denied")

    complaints = Complaint.objects.filter(
        user=request.user,
        is_hidden_from_user=False
    ).order_by("-created_at")

    context = {

        "total": complaints.count(),

        "pending": complaints.filter(
            status="pending"
        ).count(),

        "in_progress": complaints.filter(
            status="in_progress"
        ).count(),

        "resolved": complaints.filter(
            status="resolved"
        ).count(),

        "recent_complaints": complaints[:5],
    }

    return render(
        request,
        "user/dashboard.html",
        context
    )


@login_required
def my_complaints(request):

    if request.user.role != "user":
        return HttpResponseForbidden("Access Denied")

    complaints = Complaint.objects.filter(
        user=request.user,
        is_hidden_from_user=False
    ).order_by("-created_at")

    return render(
        request,
        "user/my_complaints.html",
        {
            "complaints": complaints
        }
    )

@login_required
def user_complaint_detail(request, pk):

    if request.user.role != "user":
        return HttpResponseForbidden("Access Denied")

    complaint = get_object_or_404(
        Complaint,
        id=pk,
        user=request.user
    )

    remarks = ComplaintRemark.objects.filter(
        complaint=complaint,
        is_public=True
    ).order_by("-created_at")

    activities = ComplaintActivity.objects.filter(
        complaint=complaint
    ).order_by("-created_at")

    return render(
        request,
        "user/complaint_detail.html",
        {
            "complaint": complaint,
            "activities": activities,
            "remarks": remarks,
        }
    )



@login_required
def track_complaint(request):

    if request.user.role != "user":
        return HttpResponseForbidden("Access Denied")

    complaint = None

    if request.method == "POST":

        tracking_number = request.POST.get("tracking_number")

        complaint = Complaint.objects.filter(
            tracking_number=tracking_number,
            user=request.user
        ).first()

    return render(
        request,
        "user/track_complaint.html",
        {
            "complaint": complaint
        }
    )


@login_required
def delete_complaint(request, pk):

    complaint = get_object_or_404(
        Complaint,
        id=pk,
        user=request.user
    )

    # Only resolved or rejected complaints can be deleted
    if complaint.status not in ["resolved", "rejected"]:
        return HttpResponseForbidden(
            "Only resolved or rejected complaints can be deleted."
        )

    # Soft delete (hide only from user)
    complaint.is_hidden_from_user = True

    
    complaint.save()

    return redirect("my_complaints")

from django.http import HttpResponse
@login_required
def complaint_receipt(request, pk):

    complaint = get_object_or_404(
        Complaint,
        id=pk,
        user=request.user
    )

    response = HttpResponse(
        content_type="application/pdf"
    )

    response["Content-Disposition"] = (
        f'attachment; filename="Complaint_{complaint.tracking_number}.pdf"'
    )

    doc = SimpleDocTemplate(response)

    styles = getSampleStyleSheet()

    story = []

    story.append(
        Paragraph("<b>SMART COMPLAINT MANAGEMENT SYSTEM</b>", styles["Title"])
    )

    story.append(
        Paragraph("Complaint Receipt", styles["Heading2"])
    )

    story.append(
        Paragraph("<br/>", styles["BodyText"])
    )

    story.append(
        Paragraph(
            f"<b>Tracking Number:</b> {complaint.tracking_number}",
            styles["BodyText"]
        )
    )

    story.append(
        Paragraph(
            f"<b>Complaint ID:</b> #{complaint.id}",
            styles["BodyText"]
        )
    )

    story.append(
        Paragraph(
            f"<b>Title:</b> {complaint.title}",
            styles["BodyText"]
        )
    )

    story.append(
        Paragraph(
            f"<b>Description:</b> {complaint.description}",
            styles["BodyText"]
        )
    )

    story.append(
        Paragraph(
            f"<b>Department:</b> {complaint.department}",
            styles["BodyText"]
        )
    )

    story.append(
        Paragraph(
            f"<b>Priority:</b> {complaint.priority.title()}",
            styles["BodyText"]
        )
    )

    story.append(
        Paragraph(
            f"<b>Status:</b> {complaint.status.title()}",
            styles["BodyText"]
        )
    )

    story.append(
        Paragraph(
            f"<b>Submitted:</b> {complaint.created_at.strftime('%d %B %Y %I:%M %p')}",
            styles["BodyText"]
        )
    )

    if complaint.resolved_at:

        story.append(
            Paragraph(
                f"<b>Resolved:</b> {complaint.resolved_at.strftime('%d %B %Y %I:%M %p')}",
                styles["BodyText"]
            )
        )

    story.append(
        Paragraph("<br/><br/>", styles["BodyText"])
    )

    story.append(
        Paragraph(
            "Thank you for using the Smart Complaint Management System.",
            styles["Italic"]
        )
    )

    doc.build(story)

    return response

from django.db.models import Avg
@login_required
def staff_profile(request):

    if request.user.role != "staff":
        return HttpResponseForbidden("Access Denied")

    staff = request.user

    total_assigned = Complaint.objects.filter(
        assigned_to=staff
    ).count()

    total_resolved = Complaint.objects.filter(
        assigned_to=staff,
        status="resolved"
    ).count()

    current_workload = Complaint.objects.filter(
        assigned_to=staff,
        status__in=["pending", "in_progress", "escalated"]
    ).count()
    average_rating = ComplaintFeedback.objects.filter(
        staff=staff
    ).aggregate(
        Avg("rating")
    )["rating__avg"]

    total_reviews = ComplaintFeedback.objects.filter(
        staff=staff
    ).count()
    resolution_rate = 0

    if total_assigned > 0:

        resolution_rate = round(
            (total_resolved / total_assigned) * 100,
            1
        )

    context = {
        "staff": staff,
        "total_assigned": total_assigned,
        "total_resolved": total_resolved,
        "current_workload": current_workload,
        "average_rating": average_rating,
        "total_reviews": total_reviews,
        "resolution_rate": resolution_rate,
    }

    return render(
        request,
        "complaints/staff/profile.html",
        context
    )



@login_required
def submit_feedback(request, pk):

    if request.user.role != "user":
        return HttpResponseForbidden("Access Denied")

    complaint = get_object_or_404(
        Complaint,
        id=pk,
        user=request.user
    )

    # Only resolved complaints can be rated
    if complaint.status != "resolved":
        return HttpResponseForbidden(
            "You can only rate resolved complaints."
        )

    # Prevent duplicate feedback
    if ComplaintFeedback.objects.filter(
        complaint=complaint
    ).exists():

        messages.info(
            request,
            "You have already submitted feedback for this complaint."
        )

        return redirect("complaint_detail", pk=complaint.id)

    if request.method == "POST":

        form = ComplaintFeedbackForm(request.POST)

        if form.is_valid():

            feedback = form.save(commit=False)

            feedback.complaint = complaint
            feedback.user = request.user
            feedback.staff = complaint.assigned_to

            feedback.save()

            messages.success(
                request,
                "Thank you for your feedback!"
            )

            return redirect("my_complaints")

    else:

        form = ComplaintFeedbackForm()

    return render(
        request,
        "user/feedback.html",
        {
            "form": form,
            "complaint": complaint,
        }
    )