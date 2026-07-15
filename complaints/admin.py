from django.contrib import admin
from .models import Complaint
from .models import ComplaintRemark

admin.site.register(Complaint)
admin.site.register(ComplaintRemark)