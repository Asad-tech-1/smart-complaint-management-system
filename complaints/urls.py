from django.urls import path
from . import views
from .views import (
    create_complaint,
    staff_complaints,
    complaint_master_detail,
    notification_list,
)

urlpatterns = [
    path('create/', create_complaint, name='create_complaint'),
    path(
    "my-complaints/",
    views.my_complaints,
    name="my_complaints",
    ),
    path('staff/', staff_complaints, name='staff_complaints'),
    path('detail/<int:pk>/', complaint_master_detail, name='complaint_master_detail'),
    path(
    "notifications/",
    notification_list,
    name="notification_list"
    ),
    path(
    "dashboard/",
    views.user_dashboard,
    name="user_dashboard"
    ),
    path(
    "user/complaint/<int:pk>/",
    views.user_complaint_detail,
    name="user_complaint_detail",
    ),
    path(
    "track/",
    views.track_complaint,
    name="track_complaint",
   ),

   path(
    "delete/<int:pk>/",
    views.delete_complaint,
    name="delete_complaint",
    ),
    path(
    "receipt/<int:pk>/",
    views.complaint_receipt,
    name="complaint_receipt",
    ),
    path(
    "profile/",
    views.staff_profile,
    name="staff_profile",
    ),
    path(
    "feedback/<int:pk>/",
    views.submit_feedback,
    name="submit_feedback",
    ),

]