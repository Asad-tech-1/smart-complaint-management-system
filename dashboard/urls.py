from django.urls import path
from .views import home
from dashboard import views

urlpatterns = [
    path('', home, name='home'),
    path("complaints/all/", views.all_complaints, name="all_complaints"),
    path("complaints/pending/", views.pending_complaints, name="pending_complaints"),
    path("complaints/in-progress/", views.in_progress_complaints, name="in_progress_complaints"),
    path("complaints/resolved/", views.resolved_complaints, name="resolved_complaints"),
    path(
    "analytics/",
    views.analytics,
    name="analytics",
    )
]