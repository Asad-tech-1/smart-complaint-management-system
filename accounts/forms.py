from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import User


from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User


DEPARTMENT_CHOICES = [

    ("Facilities", "Facilities"),
    ("HR", "HR"),
    ("IT", "IT"),
    ("Finance", "Finance"),
    ("Security", "Security"),
    ("General", "General"),

]


class RegisterForm(UserCreationForm):

    department = forms.ChoiceField(
        choices=DEPARTMENT_CHOICES,
        widget=forms.Select(attrs={
            "class": "form-select"
        })
    )

    class Meta:

        model = User

        fields = [

            "username",
            "first_name",
            "last_name",
            "email",
            "department",
            "phone",
            "profile_image",
            "password1",
            "password2",

        ]

        widgets = {

            "username": forms.TextInput(attrs={
                "class": "form-control"
            }),

            "first_name": forms.TextInput(attrs={
                "class": "form-control"
            }),

            "last_name": forms.TextInput(attrs={
                "class": "form-control"
            }),

            "email": forms.EmailInput(attrs={
                "class": "form-control"
            }),

            "phone": forms.TextInput(attrs={
                "class": "form-control"
            }),

            "profile_image": forms.ClearableFileInput(attrs={
                "class": "form-control"
            }),

        }

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.fields["password1"].widget.attrs.update({
            "class": "form-control"
        })

        self.fields["password2"].widget.attrs.update({
            "class": "form-control"
        })

    def save(self, commit=True):

        user = super().save(commit=False)

        user.role = "staff"

        if commit:
            user.save()

        return user
    



class UserRegisterForm(UserCreationForm):

    class Meta:

        model = User

        fields = [
            "username",
            "first_name",
            "last_name",
            "email",
            "phone",
            "profile_image",
            "password1",
            "password2",
        ]

        widgets = {

            "username": forms.TextInput(attrs={
                "class": "form-control"
            }),

            "first_name": forms.TextInput(attrs={
                "class": "form-control"
            }),

            "last_name": forms.TextInput(attrs={
                "class": "form-control"
            }),

            "email": forms.EmailInput(attrs={
                "class": "form-control"
            }),

            "phone": forms.TextInput(attrs={
                "class": "form-control"
            }),

            "profile_image": forms.ClearableFileInput(attrs={
                "class": "form-control"
            }),

        }

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.fields["password1"].widget.attrs.update({
            "class": "form-control"
        })

        self.fields["password2"].widget.attrs.update({
            "class": "form-control"
        })

    def save(self, commit=True):

        user = super().save(commit=False)

        # Every self-registering account is a normal user
        user.role = "user"

        if commit:
            user.save()

        return user



# =========================
# UPDATE EMPLOYEE
# =========================

class EmployeeForm(forms.ModelForm):

    class Meta:

        model = User

        fields = [

            "username",

            "first_name",

            "last_name",

            "email",

            "department",

            "phone",

            "profile_image",

            "is_active",

        ]

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            field.widget.attrs.update({
                "class": "form-control"
            })