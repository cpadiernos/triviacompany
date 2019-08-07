import datetime
from django import forms
from .models import Reimbursement

class ReimbursementForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(ReimbursementForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].required = True
        
    class Meta:
        model = Reimbursement
        fields = (
            'purchase_date', 'category', 'description', 'amount',
            'documentation')