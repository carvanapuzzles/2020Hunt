from django import forms
from django.contrib.auth.models import User
from hunt20.models import Team
from django.contrib.auth.forms import UserCreationForm

class UserRegisterForm(UserCreationForm):
    team_name = forms.CharField(label="Team Name", help_text="How your team will appear on the public leaderboard")
    #username = forms.CharField(label="Username", help_text="Short, private, name you will use to login")
    email = forms.EmailField(label="Captain's Email")
    team_captain = forms.CharField(label="Team Captain", help_text="Should be a Carvana employee")
    
    field_order=['team_name','username','team_captain','email','password1','password2']
    class Meta:
        model = User
        fields = ['username','email','password1','password2']
        help_texts = {
            'username': 'Shorter, private name your ENTIRE TEAM will share and use to login (do not use your Carvana username/password)',
        }

class AddMemberForm(forms.ModelForm):
    member = forms.CharField(required=True, label="Team member's name")

    class Meta:
        model = Team
        fields = ['member']