from django import forms
from .models import Complaint, ComplaintFeedback
from .models import ComplaintFeedback

class ComplaintForm(forms.ModelForm):
    class Meta:
        model = Complaint
        fields = ['title', 'description', 'attachment']




class ComplaintFeedbackForm(forms.ModelForm):

    class Meta:

        model = ComplaintFeedback

        fields = [
            "rating",
            "comment",
        ]

        widgets = {

            "rating": forms.Select(
                choices=[
                    (5, "★★★★★ Excellent"),
                    (4, "★★★★☆ Good"),
                    (3, "★★★☆☆ Average"),
                    (2, "★★☆☆☆ Poor"),
                    (1, "★☆☆☆☆ Very Poor"),
                ],
                attrs={
                    "class": "form-control"
                }
            ),

            "comment": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 5,
                    "placeholder": "Share your experience (optional)..."
                }
            ),
        }