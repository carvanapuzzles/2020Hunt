from django import forms
from django.db.models import Q
from .models import Submission
from .models import HintRequest
from .models import Puzzle
from django.contrib.auth.models import User


class SubmitForm(forms.ModelForm):
    team_ans = forms.CharField(label="Your Answer:", strip=True)
    field_order = ['team_ans']
    class Meta:
        model = Submission
        fields = ['team_ans']

class HintForm(forms.ModelForm):
    team_question = forms.CharField(widget=forms.Textarea(attrs={'width':"100%",'rows': "6", }),label="Hint Request")
    class Meta:
        model = HintRequest
        fields = ['puzzle_name','team_question']

    def __init__(self, user, *args, **kwargs):
        super(HintForm, self).__init__(*args, **kwargs)
        current_round = user.team.in_round
        self.fields['puzzle_name'] = forms.ModelChoiceField(
                                     queryset=Puzzle.objects.exclude(puzzle_id__in=Submission.objects.filter(correct=True).filter(username=user.username).values_list('puzzle__puzzle_id', flat=True)).filter(Q(in_round__lt=current_round) | (Q(in_round=current_round) & Q(unlocks_at__lte=user.team.round_solves(current_round))))
                                     )