from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import UserRegisterForm #, AddMemberForm
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from hunt20.models import Team
from hunt20.models import Submission
from django.contrib.auth.models import User

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.refresh_from_db()
            team_name = form.cleaned_data.get('team_name')
            user.team.name = team_name
            user.save()
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=user.username, password=raw_password)
            login(request, user)
            messages.success(request, f'{team_name} successfully registered!')
            return redirect('hunt20-home')
    else:
        form = UserRegisterForm()
    return render(request, 'users/register.html', {'form': form})


