import re
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.utils import timezone
from django.db.models import Q
from .models import Team
from .models import Submission
from .models import Puzzle
from .models import HintRequest
from .forms import SubmitForm
from .forms import HintForm
from django_slack import slack_message


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

def leaderboard(request):
    context = {
        'teams': sorted(sorted(Team.objects.filter(username__is_superuser=False).filter(is_testsolver=False),key=lambda b: b.last_solve_datetime ), key=lambda a: a.total_solves, reverse=True), 
    }
    return render(request, 'hunt20/leaderboard.html', context)

def bigboard(request):
    if request.user.is_superuser is False:
        return redirect('hunt20-invalid')
    else:
        context = {
            'teams': sorted(sorted(Team.objects.filter(username__is_superuser=False).filter(is_testsolver=False), key=lambda b: b.last_solve_datetime),key=lambda a: a.total_solves, reverse=True),
            'puzzles': sorted(Puzzle.objects.all(),key=lambda b: b.puzzle_id),
        }
        return render(request, 'hunt20/bigboard.html', context)

def puzzles(request):
    context = {
        'puzzles': sorted(Puzzle.objects.all(),key=lambda b: b.puzzle_id),
        'in_round': request.user.team.in_round,
    }
    return render(request, 'hunt20/puzzles.html', context)

def round_archives(request, round_num):
    if int(round_num) > request.user.team.in_round:
        return redirect('hunt20-invalid')
    else:
        context = {
            'puzzles': sorted(Puzzle.objects.filter(in_round=round_num).filter(unlocks_at__lte=request.user.team.round_solves(round_num)),key=lambda b: b.puzzle_id),
            'solved_ids': Submission.objects.filter(correct=True).filter(username=request.user.username).values_list('puzzle__puzzle_id', flat=True),
        }
        return render(request, 'hunt20/puzzles/r' + round_num + '.html', context)

def puzzle_archives(request, puzzle_id):
    puzzle = Puzzle.objects.filter(puzzle_id=puzzle_id).first()
    
    if (int(puzzle.in_round) > request.user.team.in_round) or (puzzle.unlocks_at > request.user.team.round_solves(puzzle.in_round)):
        return redirect('hunt20-invalid')

    else:
        submissions = Submission.objects.filter(puzzle__puzzle_id=puzzle_id).filter(username=request.user.username)
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

    puzzle = Puzzle.objects.filter(puzzle_id=puzzle_id).first()

    if STATUS == "pre" and request.user.team.is_testsolver is False and request.user.is_superuser is False:
        return redirect('hunt20-invalid')

    elif (int(puzzle.in_round) > request.user.team.in_round) or (puzzle.unlocks_at > request.user.team.round_solves(puzzle.in_round)):
        return redirect('hunt20-invalid')
    
    else:
        round = Puzzle.objects.get(puzzle_id=puzzle_id).in_round
        submit_html = 'hunt20/puzzles/submit'+str(round)+'.html'

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
                    submission.puzzle = Puzzle.objects.get(puzzle_id=puzzle_id)
                    submission.eventdatetime = timezone.now()
                    submission.team_ans = normalize(submission.team_ans)
                    norm_ans = normalize(Puzzle.objects.get(puzzle_id=puzzle_id).puzzle_ans)
                    norm_cluephrase = normalize(Puzzle.objects.get(puzzle_id=puzzle_id).puzzle_cluephrase)
                    norm_midpoint = normalize(Puzzle.objects.get(puzzle_id=puzzle_id).puzzle_midpoint)
                    # print(norm_ans)


                    if Submission.objects.filter(puzzle__puzzle_id=puzzle_id).filter(username=request.user.username).filter(team_ans=submission.team_ans).exists():
                        messages.warning(request, 'You have already submitted this answer')
                        return redirect('hunt20-submit', puzzle_id=puzzle_id)
                    
                    elif norm_ans==submission.team_ans:
                        submission.correct = True
                        result = 'Correct!'
                        submission = form.save()
                        messages.success(request, 'Correct!')
                        
                    elif norm_cluephrase==submission.team_ans and norm_cluephrase!="DNE":
                        submission.correct = False
                        result = 'Cluephrase'
                        submission = form.save()
                        messages.warning(request, 'That is the final cluephrase for this puzzle!')
                    
                    elif norm_midpoint==submission.team_ans and norm_midpoint!="DNE":
                        submission.correct = False
                        result = 'Midpoint'
                        submission = form.save()
                        messages.warning(request, 'On the right track! But you need to do a little more in the puzzle')

                    else:    
                        submission.correct = False
                        result = 'Incorrect'
                        submission = form.save()
                        messages.error(request, 'Incorrect')

                    slack_message('hunt20/submission.slack',{
                        'guess':submission.team_ans,
                        'team':request.user.team.name,
                        'puzzle':Puzzle.objects.get(puzzle_id=puzzle_id).puzzle_name,
                        'result':result,
                        'emoji':'squirrel',
                    })

                    return redirect('hunt20-submit', puzzle_id=puzzle_id)
        else:
            form = SubmitForm()
        
        submissions = Submission.objects.filter(puzzle__puzzle_id=puzzle_id).filter(username=request.user.username)
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

@login_required
def hints(request):
    # STATUS = get_hunt_status()
    if request.method == 'POST':
        form = HintForm(user = request.user, data = request.POST)
        if form.is_valid():
            submission = form.save(commit=False)
            submission.username = request.user.username
            submission.eventdatetime = timezone.now()
            submission.answered = False
            submission = form.save()
            messages.success(request, 'Hint request submitted!')
            

            slack_message('hunt20/hint.slack',{
                'question':submission.team_question,
                'team':request.user.team.name,
                'puzzle':submission.puzzle_name,
                'emoji':'squirrel',
                    })

            return redirect('hunt20-hints')

    else:
        form = HintForm(user=request.user)

    context = {
        'hints': sorted(HintRequest.objects.filter(username=request.user.username), key=lambda b: b.eventdatetime, reverse=True),
        'form': form,
        'open_puzzles': Puzzle.objects.filter(Q(in_round__lte=request.user.team.in_round)),
        'hints_available' : 10 - HintRequest.objects.filter(username=request.user.username).filter(refunded=False).count(),
        # 'status' : STATUS,
        'testsolver': request.user.team.is_testsolver,
    }      
    return render(request, 'hunt20/hints.html', context=context)