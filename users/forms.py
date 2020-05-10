from django import forms
from django.contrib.auth.models import User
from hunt20.models import Team
from django.contrib.auth.forms import UserCreationForm

class UserRegisterForm(UserCreationForm):
    team_name = forms.CharField(label="Team Name", help_text="How your team will appear on the public leaderboard")
    #username = forms.CharField(label="Username", help_text="Short, private, name you will use to login")
    email = forms.EmailField(label="Captain's Email")
    
    field_order=['team_name','username','email','password1','password2']
    class Meta:
        model = User
        fields = ['username','email','password1','password2']
        help_texts = {
            'username': 'Shorter, private name you will use to login. Your entire team will use this name and password to login!',
        }