from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import UserRegisterForm, AddMemberForm
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from hunt20.models import Team
from hunt20.models import Submission
from django.contrib.auth.models import User
from django_slack import slack_message
from hunt20.globals import get_background

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.refresh_from_db()
            team_name = form.cleaned_data.get('team_name')
            user.team.name = team_name
            captain = form.cleaned_data.get('team_captain')
            user.team.captain = captain
            user.save()
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=user.username, password=raw_password)
            login(request, user)
            messages.success(request, f'{team_name} successfully registered!')


            slack_message('users/reg.slack',{
                'captain':captain,
                'team': team_name,
                'emoji':'squirrel',
            })

            return redirect('hunt20-home')

    else:
        form = UserRegisterForm()
    return render(request, 'users/register.html', {'form': form})

@login_required
def team(request, user_pk):
    bg = get_background(request)
    if request.method == 'POST':
        form = AddMemberForm(request.POST, instance=request.user.team)
        if form.is_valid():
            team = form.save(commit=False)
            new_mem = form.cleaned_data.get('member')
            if team.member1 == 'DNE':
                team.member1 = new_mem
            elif team.member2 == 'DNE':
                team.member2 = new_mem
            elif team.member3 == 'DNE':
                team.member3 = new_mem
            elif team.member4 == 'DNE':
                team.member4 = new_mem
            else:
                team.member5 = new_mem
            team.save()
            messages.success(request, f'{new_mem} successfully added!')
            return redirect('hunt20-team', user_pk=user_pk)
    else:
        form = AddMemberForm(instance=request.user.team)
                
    context = {
        'displayteam': Team.objects.filter(username__pk=user_pk).first(),
        'form' : form,
        'background' : bg
    }
    return render(request, 'users/team.html', context = context)


