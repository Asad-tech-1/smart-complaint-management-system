from urllib import request

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.db.models import Count
from .forms import UserRegisterForm
from .forms import RegisterForm, EmployeeForm
from .models import User
from complaints.models import Complaint
from complaints.models import Complaint, Notification
import accounts.emails
# =========================
# REGISTER STAFF (ADMIN ONLY)
# =========================
@login_required
def register(request):

    # Only Admin can create staff accounts
    if request.user.role != "admin":
        return HttpResponseForbidden("Access Denied")

    if request.method == "POST":

        form = RegisterForm(request.POST)

        if form.is_valid():

            # Save Staff Account
            form.save()

            # Admin stays logged in
            # Redirect will be changed later when Employee Module is built
            return redirect("home")

    else:

        form = RegisterForm()

    return render(
        request,
        "accounts/register.html",
        {
            "form": form
        }
    )


# =========================
# LOGIN
# =========================
def user_login(request):

        # Already logged in?
    if request.user.is_authenticated:

        if request.user.role == "admin":
            return redirect("home")

        elif request.user.role == "staff":
            return redirect("staff_complaints")

        elif request.user.role == "user":
            return redirect("user_dashboard")

        logout(request)
        return redirect("login")

    if request.method == "POST":

        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:

            # Allow all valid roles
            if user.role not in ["admin", "staff", "user"]:

                return render(
                    request,
                    "accounts/login.html",
                    {
                        "error": "This account is not allowed to log in."
                    }
                )

            login(request, user)

            if user.role == "admin":
                return redirect("home")

            elif user.role == "staff":
                return redirect("staff_complaints")
            
            elif user.role == "user":
                return redirect("user_dashboard")

        return render(
            request,
            "accounts/login.html",
            {
                "error": "Invalid username or password."
            }
        )

    return render(
        request,
        "accounts/login.html"
    )


# =========================
# LOGOUT
# =========================
@login_required
def user_logout(request):

    logout(request)

    return redirect("login")



# ===================================
# EMPLOYEE LIST
# ===================================
from django.db.models import Count, Avg, Q
from complaints.models import ComplaintFeedback
@login_required
def employee_list(request):

    if request.user.role != "admin":
        return HttpResponseForbidden("Access Denied")

    search = request.GET.get("search")

    employees = User.objects.filter(
        role="staff"
    ).annotate(

        workload=Count(
            "assigned_complaints",
            filter=Q(
                assigned_complaints__status__in=[
                    "pending",
                    "in_progress",
                    "escalated"
                ]
            )
        ),

        total_assigned=Count(
            "assigned_complaints",
            distinct=True
        ),

        total_resolved=Count(
            "assigned_complaints",
            filter=Q(
                assigned_complaints__status="resolved"
            ),
            distinct=True
        ),

        average_rating=Avg(
            "feedbacks_received__rating"
        ),

        total_reviews=Count(
            "feedbacks_received",
            distinct=True
        )

    )

    if search:
        employees = employees.filter(
            username__icontains=search
        )

    for employee in employees:

        if employee.total_assigned > 0:

            employee.resolution_rate = round(
                employee.total_resolved * 100 /
                employee.total_assigned,
                1
            )

        else:

            employee.resolution_rate = 0    

    return render(
        request,
        "accounts/employee_list.html",
        {
            "employees": employees
        }
    )


# ===================================
# CREATE EMPLOYEE
# ===================================

@login_required
def employee_create(request):

    if request.user.role != "admin":
        return HttpResponseForbidden("Access Denied")

    if request.method == "POST":

        form = RegisterForm(
            request.POST,
            request.FILES
        )

        if form.is_valid():

            form.save()

            return redirect("employee_list")

    else:

        form = RegisterForm()

    return render(
        request,
        "accounts/register.html",
        {
            "form": form
        }
    )


# ===================================
# UPDATE EMPLOYEE
# ===================================

@login_required
def employee_update(request, pk):

    if request.user.role != "admin":
        return HttpResponseForbidden("Access Denied")

    employee = get_object_or_404(
        User,
        pk=pk,
        role="staff"
    )

    if request.method == "POST":

        form = EmployeeForm(
            request.POST,
            request.FILES,
            instance=employee
        )

        if form.is_valid():

            form.save()

            return redirect("employee_list")

    else:

        form = EmployeeForm(
            instance=employee
        )

    return render(
        request,
        "accounts/employee_edit.html",
        {
            "form": form,
            "employee": employee
        }
    )


# ===================================
# DELETE EMPLOYEE
# ===================================

@login_required
def employee_delete(request, pk):

    if request.user.role != "admin":
        return HttpResponseForbidden("Access Denied")

    employee = get_object_or_404(
        User,
        pk=pk,
        role="staff"
    )

    if request.method == "POST":

        employee.delete()

        return redirect("employee_list")

    return render(
        request,
        "accounts/employee_delete.html",
        {
            "employee": employee
        }
    )



from django.contrib import messages
from django.shortcuts import render, redirect

def user_register(request):

    if request.method == "POST":

        form = UserRegisterForm(request.POST, request.FILES)

        if form.is_valid():

            user = form.save()
            accounts.emails.send_welcome_email(user)
            messages.success(
                request,
                "Your account has been created successfully."
            )

            return redirect("login")

        else:
            messages.error(
                request,
                "An account with this username or email already exists."
            )

    else:
        form = UserRegisterForm()

    return render(
        request,
        "accounts/user_register.html",
        {
            "form": form
        }
    )