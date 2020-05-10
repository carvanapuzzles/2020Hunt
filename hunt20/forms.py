from django import forms
from .models import Submission
# from .models import HintRequest
from .models import Puzzle
from django.contrib.auth.models import User


class SubmitForm(forms.ModelForm):
    team_ans = forms.CharField(label="Your Answer:", strip=True)
    field_order = ['team_ans']
    class Meta:
        model = Submission
        fields = ['team_ans']