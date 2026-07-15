from django.db import models
from accounts.models import User


class Complaint(models.Model):

    tracking_number = models.CharField(
    max_length=30,
    unique=True,
    blank=True,
    null=True
    )

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('rejected', 'Rejected'),
        ('escalated', 'Escalated'),
    ]

    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]

    # 👤 Who created the complaint
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="complaints"
    )

    title = models.CharField(max_length=255)
    description = models.TextField()

    # 🧠 AI output fields
    department = models.CharField(max_length=100, blank=True, null=True)
    priority = models.CharField(
        max_length=10,
        choices=PRIORITY_CHOICES,
        default='low'
    )

    # 👨‍💼 FIXED: proper staff assignment (IMPORTANT CHANGE)
    assigned_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_complaints"
    )

    # 👨‍💼 Original staff before escalation
    escalated_from = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="escalated_complaints"
    )

    # 📌 workflow tracking
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )

    

    attachment = models.ImageField(
        upload_to='complaints/',
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    sla_deadline = models.DateTimeField(
    null=True,
    blank=True
    )

    is_overdue = models.BooleanField(
        default=False
    )

    escalation_level = models.IntegerField(
        default=0
    )

    resolved_at = models.DateTimeField(
        null=True,
        blank=True
    )

    completed_at = models.DateTimeField(
    null=True,
    blank=True
    )

    is_hidden_from_user = models.BooleanField(default=False)

    is_hidden_from_staff = models.BooleanField(default=False)

    is_hidden_from_admin = models.BooleanField(default=False)

    hidden_from_admin_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.title} - {self.status}"
    

class ComplaintActivity(models.Model):

    # 🎯 EVENT TYPES (CORE UPGRADE)
    EVENT_TYPES = [
        ('created', 'Created'),
        ('ai_assigned', 'AI Assigned'),
        ('assigned', 'Assigned'),
        ('reassigned', 'Reassigned'),
        ('status_changed', 'Status Changed'),
        ('remarks_added', 'Remarks Added'),
        ('resolved', 'Resolved'),
        ('sla_created', 'SLA Created'),
        ('overdue', 'Overdue'),
        ('escalated', 'Escalated'),
    ]

    complaint = models.ForeignKey(
        Complaint,
        on_delete=models.CASCADE,
        related_name='activities'
    )

    event_type = models.CharField(
        max_length=30,
        choices=EVENT_TYPES
    )

    message = models.TextField()

    performed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.complaint.title} - {self.event_type}"    
    


class Notification(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="notifications"
    )

    title = models.CharField(max_length=255)

    is_read = models.BooleanField(
        default=False
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.title
    


class ComplaintComment(models.Model):
    complaint = models.ForeignKey(
        Complaint,
        on_delete=models.CASCADE,
        related_name="comments"
    )

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    message = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)



class ComplaintRemark(models.Model):

    complaint = models.ForeignKey(
        Complaint,
        on_delete=models.CASCADE,
        related_name="remarks"
    )

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    message = models.TextField()

    is_public = models.BooleanField(
        default=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Remark for Complaint #{self.complaint.id}"
    

class ComplaintFeedback(models.Model):

    complaint = models.OneToOneField(
        Complaint,
        on_delete=models.CASCADE,
        related_name="feedback"
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="feedbacks_given"
    )

    staff = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="feedbacks_received"
    )

    rating = models.PositiveSmallIntegerField()

    comment = models.TextField(
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.complaint.tracking_number} - {self.rating} Stars"