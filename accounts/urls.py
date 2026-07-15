from django.urls import path, reverse_lazy
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [

    # Authentication


    path(
    "signup/",
    views.user_register,
    name="user_register"
    ),

    path(
        "login/",
        views.user_login,
        name="login"
    ),

    path(
        "logout/",
        views.user_logout,
        name="logout"
    ),

    path(
        "register/",
        views.register,
        name="register"
    ),
    # ==========================
    # PASSWORD RESET
    # ==========================

    path(
        "password-reset/",
        auth_views.PasswordResetView.as_view(
            template_name="accounts/password_reset.html",
            email_template_name="accounts/password_reset_email.html",
            subject_template_name="accounts/password_reset_subject.txt",
            success_url=reverse_lazy("password_reset_done"),
        ),
        name="password_reset",
    ),

    path(
        "password-reset/done/",
        auth_views.PasswordResetDoneView.as_view(
            template_name="accounts/password_reset_done.html",
        ),
        name="password_reset_done",
    ),

    path(
        "reset/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="accounts/password_reset_confirm.html",
        ),
        name="password_reset_confirm",
    ),

    path(
        "reset/done/",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="accounts/password_reset_complete.html",
        ),
        name="password_reset_complete",
    ),

    # Employee Management

    path(
        "employees/",
        views.employee_list,
        name="employee_list"
    ),

    path(
    "employees/add/",
    views.employee_create,
    name="employee_create"
    ),

    path(
        "employees/<int:pk>/edit/",
        views.employee_update,
        name="employee_update"
    ),

    path(
        "employees/<int:pk>/delete/",
        views.employee_delete,
        name="employee_delete"
    ),

]