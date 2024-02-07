from django.forms import ModelForm
from .models import Workshop

class WorkshopForm(ModelForm):
    class Meta:
        model = Workshop
        fields = ['workshop_title', 'workshop_summary']