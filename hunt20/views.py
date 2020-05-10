import re
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.utils import timezone
from .models import Team
from .models import Submission
from .models import Puzzle
# from .models import HintRequest
from .forms import SubmitForm


def home(request):
    context = {}
    return render(request, 'hunt20/home.html', context)

def invalid(request):
    return render(request, 'hunt20/invalid.html')    

def about(request):
    return render(request, 'hunt20/about.html')

def faq(request):
    return render(request, 'hunt20/faq.html')

def guide(request):
    return render(request, 'hunt20/guide.html')

def puzzles(request):
    context = {
        'puzzles': Puzzle.objects.all()
    }
    return render(request, 'hunt20/puzzles.html', context)

def puzzle_archives(request, puzzle_id):
    submissions = Submission.objects.filter(puzzle_id=puzzle_id).filter(username=request.user.username)
    if submissions.filter(correct=True).exists():
        solved = True
    else:
        solved = False
    context = {
        'teams': Team.objects.all(),
        'puzzle_id': puzzle_id,
        'puzzle': Puzzle.objects.filter(puzzle_id=puzzle_id).first(),
        'solved': solved,
        'status': "active", # change later
    }
    puzzle_html = 'hunt20/puzzles/' + puzzle_id + '.html'
    return render(request, puzzle_html, context)

def solution_archives(request, puzzle_id):
    
    context = {
        'puzzle_id': puzzle_id,
        'puzzle': Puzzle.objects.filter(puzzle_id=puzzle_id).first(),
    }
    sol_html = 'hunt20/puzzles/' + puzzle_id + '_sol.html'
    return render(request, sol_html, context)

@login_required
def submit(request, puzzle_id):
    STATUS = "active"

    power = request.user.team.total_solves

    if STATUS == "pre" and request.user.team.is_testsolver is False and request.user.is_superuser is False:
        return redirect('hunt20-invalid')

    elif power<Puzzle.objects.get(puzzle_id=puzzle_id).unlocks_at:
        return redirect('hunt20-invalid')
    
    else:

        submit_html = 'hunt20/puzzles/submit.html'

        def normalize(ans):
            regex = re.compile('[^a-zA-Z]')
            return regex.sub('', ans).upper()

        if request.method == 'POST':
            
            if STATUS == "post":
                messages.error(request, 'Hunt is over!')
                return redirect('hunt20-submit', puzzle_id=puzzle_id)
            
            else:

                form = SubmitForm(request.POST)
                if form.is_valid():
                    submission = form.save(commit=False)
                    submission.username = request.user.username
                    submission.puzzle_id = puzzle_id
                    submission.eventdatetime = timezone.now()
                    submission.team_ans = normalize(submission.team_ans)
                    norm_ans = normalize(Puzzle.objects.get(puzzle_id=puzzle_id).puzzle_ans)
                    # print(norm_ans)


                    if Submission.objects.filter(puzzle_id=puzzle_id).filter(username=request.user.username).filter(team_ans=submission.team_ans).exists():
                        messages.warning(request, 'You have already submitted this answer')
                        return redirect('hunt20-submit', puzzle_id=puzzle_id)
                    
                    elif norm_ans==submission.team_ans:
                        submission.correct = True
                        submission = form.save()
                        messages.success(request, 'Correct!')

                    else:    
                        submission.correct = False
                        submission = form.save()
                        messages.error(request, 'Incorrect')
                    
                    return redirect('hunt20-submit', puzzle_id=puzzle_id)
        else:
            form = SubmitForm()
        
        submissions = Submission.objects.filter(puzzle_id=puzzle_id).filter(username=request.user.username)
        if submissions.filter(correct=True).exists():
            solved = True
        else:
            solved = False
        context = {
            'teams': Team.objects.all(),
            'puzzle_id': puzzle_id,
            'form': form,
            'submissions': submissions,
            'guesses_left': max(25-len(submissions),0),
            'puzzle': Puzzle.objects.filter(puzzle_id=puzzle_id).first(),
            'solved': solved,
        }      
        return render(request, submit_html, context=context)