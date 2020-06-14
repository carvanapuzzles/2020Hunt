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
from .globals import get_background, get_hunt_status, get_avail_hints
from django.http import JsonResponse

def home(request):
    STATUS = get_hunt_status()
    bg = get_background(request)
    context = {
        'background': bg,
        'status': STATUS,
    }
    return render(request, 'hunt20/home.html', context)

def invalid(request):
    bg = get_background(request)
    context = {
        'background': bg
    }
    return render(request, 'hunt20/invalid.html', context)    

def about(request):
    bg = get_background(request)
    context = {
        'background': bg
    }
    return render(request, 'hunt20/about.html', context)

def faq(request):
    bg = get_background(request)
    context = {
        'background': bg
    }
    return render(request, 'hunt20/faq.html', context)

def guide(request):
    bg = get_background(request)
    context = {
        'background': bg
    }
    return render(request, 'hunt20/guide.html', context)

def error_404(request, exception):
    return render(request,'hunt20/invalid.html', status = 404)

def error_500(request):
    return render(request,'hunt20/error.html', status = 500)

def leaderboard(request):
    bg = get_background(request)
    context = {
        'teams': sorted(sorted(Team.objects.filter(username__is_superuser=False).filter(is_testsolver=False),key=lambda b: b.last_solve_datetime ), key=lambda a: a.total_solves, reverse=True), 
        'background': bg
    }
    return render(request, 'hunt20/leaderboard.html', context)

def bigboard(request):
    if request.user.is_superuser is False:
        return redirect('hunt20-invalid')
    else:
        context = {
            'teams': sorted(sorted(Team.objects.filter(username__is_superuser=False).filter(is_testsolver=False), key=lambda b: b.last_solve_datetime),key=lambda a: a.total_solves, reverse=True),
            'puzzles1': sorted(Puzzle.objects.filter(in_round=1),key=lambda b: b.puzzle_id),
            'puzzles2': sorted(Puzzle.objects.filter(in_round=2),key=lambda b: b.puzzle_id),
            'puzzles3': sorted(Puzzle.objects.filter(in_round=3),key=lambda b: b.puzzle_id),
        }
        return render(request, 'hunt20/bigboard.html', context)

@login_required
def puzzles(request):
    STATUS = get_hunt_status()
    bg = get_background(request)
    context = {
        'puzzles': sorted(Puzzle.objects.all(),key=lambda b: b.puzzle_id),
        'in_round': request.user.team.in_round,
        'background': bg,
        'status': STATUS,
    }
    return render(request, 'hunt20/puzzles.html', context)

@login_required
def round_archives(request, round_num):
    STATUS = get_hunt_status()
    if STATUS=='post':
        context = {
            'puzzles': sorted(Puzzle.objects.filter(in_round=round_num),key=lambda b: b.puzzle_id),
            'solved_ids': Submission.objects.filter(correct=True).filter(username=request.user.username).values_list('puzzle__puzzle_id', flat=True),
        }
        return render(request, 'hunt20/puzzles/r' + round_num + '.html', context)
    
    elif int(round_num) > request.user.team.in_round or (STATUS=='pre' and request.user.is_superuser is False):
        return redirect('hunt20-invalid')
    
    else:
        context = {
            'puzzles': sorted(Puzzle.objects.filter(in_round=round_num).filter(unlocks_at__lte=request.user.team.round_solves(round_num)),key=lambda b: b.puzzle_id),
            'solved_ids': Submission.objects.filter(correct=True).filter(username=request.user.username).values_list('puzzle__puzzle_id', flat=True),
        }
        return render(request, 'hunt20/puzzles/r' + round_num + '.html', context)

@login_required
def puzzle_archives(request, puzzle_id):
    STATUS = get_hunt_status()
    puzzle = Puzzle.objects.filter(puzzle_id=puzzle_id).first()

    if STATUS=='post':
        context = {
            'teams': Team.objects.all(),
            'puzzle_id': puzzle_id,
            'puzzle': Puzzle.objects.filter(puzzle_id=puzzle_id).first(),
            'solved': False,
            'status': STATUS,
        }
        puzzle_html = 'hunt20/puzzles/' + puzzle_id + '.html'
        return render(request, puzzle_html, context)

    elif (STATUS=='pre' and request.user.is_superuser is False) or ((int(puzzle.in_round) > request.user.team.in_round) or (puzzle.unlocks_at > request.user.team.round_solves(puzzle.in_round))):
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
            'status': STATUS, # change later
        }
        puzzle_html = 'hunt20/puzzles/' + puzzle_id + '.html'
        return render(request, puzzle_html, context)

@login_required
def solution_archives(request, puzzle_id):
    
    context = {
        'puzzle_id': puzzle_id,
        'puzzle': Puzzle.objects.filter(puzzle_id=puzzle_id).first(),
    }
    sol_html = 'hunt20/puzzles/' + puzzle_id + '_sol.html'
    return render(request, sol_html, context)

@login_required
def submit(request, puzzle_id):
    STATUS = get_hunt_status()

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
                        msg_emoji = ':white_check_mark:'
                        
                    elif norm_cluephrase==submission.team_ans and norm_cluephrase!="DNE":
                        submission.correct = False
                        result = 'Cluephrase'
                        submission = form.save()
                        messages.warning(request, 'That is the final cluephrase for this puzzle!')
                        msg_emoji = ':thinking_face:'
                    
                    elif norm_midpoint==submission.team_ans and norm_midpoint!="DNE":
                        submission.correct = False
                        result = 'Midpoint'
                        submission = form.save()
                        messages.warning(request, 'On the right track! But you need to do a little more in the puzzle')
                        msg_emoji = ':point_right:'

                    else:    
                        submission.correct = False
                        result = 'Incorrect'
                        submission = form.save()
                        messages.error(request, 'Incorrect')
                        msg_emoji = ':x:'

                    slack_message('hunt20/submission.slack',{
                        'guess':submission.team_ans,
                        'team':request.user.team.name,
                        'puzzle':Puzzle.objects.get(puzzle_id=puzzle_id).puzzle_name,
                        'result':result,
                        'emoji':'squirrel',
                        'msg_emoji': msg_emoji
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
    HINTS = get_avail_hints()
    bg = get_background(request)
    STATUS = get_hunt_status()
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
        'hints_available' : HINTS - HintRequest.objects.filter(username=request.user.username).filter(refunded=False).count(),
        'testsolver': request.user.team.is_testsolver,
        'background': bg,
        'status': STATUS,
    }      
    return render(request, 'hunt20/hints.html', context=context)

def insanity_check(request):
    s = request.GET.get("inputs")
    if s[-83:]=='1'*83:
        if len(s)==83:
            output = '~A~'
        elif s[-84]!='1':
            output = '~A~'
        else:
            output = 'I'
    elif s[-69:]=='2'*69:
        if len(s)==69:
            output = '~S~'
        elif s[-70]!='2':
            output = '~S~'
        else:
            output = 'N'
    elif s[-84:]=='3'*84:
        if len(s)==84:
            output = '~C~'
        elif s[-85]!='3':
            output = '~C~'
        else:
            output = 'S'
    elif s[-79:]=='4'*79:
        if len(s)==79:
            output = '~I~'
        elif s[-80]!='4':
            output = '~I~'
        else:
            output = 'A'
    elif s[-70:]=='5'*70:
        if len(s)==70:
            output = '~I~'
        elif s[-71]!='5':
            output = '~I~'
        else:
            output = 'N'
    elif s[-50:]=='6'*50:
        if len(s)==50:
            output = '~!~'
        elif s[-51]!='6':
            output = '~!~'
        else:
            output = 'E'
    #round2
    elif s[-28:]=='12'*14:
        if len(s)<30:
            output = '~S~'
        elif s[-30:-28]!='12':
            output = '~S~'
        else:
            output = 'N'
    elif s[-30:]=='13'*15:
        if len(s)<32:
            output = '~O~'
        elif s[-32:-30]!='13':
            output = '~O~'
        else:
            output = 'S'
    elif s[-46:]=='14'*23:
        if len(s)<48:
            output = '~C~'
        elif s[-48:-46]!='14':
            output = '~C~'
        else:
            output = 'A'
    elif s[-38:]=='15'*19:
        if len(s)<40:
            output = '~R~'
        elif s[-40:-38]!='15':
            output = '~R~'
        else:
            output = 'N'
    elif s[-32:]=='16'*16:
        if len(s)<34:
            output = '~A~'
        elif s[-34:-32]!='16':
            output = '~A~'
        else:
            output = 'E'
    elif s[-10:]=='23'*5:
        if len(s)<12:
            output = '~Z~'
        elif s[-12:-10]!='23':
            output = '~Z~'
        else:
            output = 'S'
    elif s[-24:]=='24'*12:
        if len(s)<26:
            output = '~Y~'
        elif s[-26:-24]!='24':
            output = '~Y~'
        else:
            output = 'A'
    elif s[-24:]=='25'*12:
        if len(s)<26:
            output = '~I~'
        elif s[-26:-24]!='25':
            output = '~I~'
        else:
            output = 'N'
    elif s[-26:]=='26'*13:
        if len(s)<28:
            output = '~A~'
        elif s[-28:-26]!='26':
            output = '~A~'
        else:
            output = 'E'
    elif s[-50:]=='34'*25:
        if len(s)<52:
            output = '~M~'
        elif s[-52:-50]!='34':
            output = '~M~'
        else:
            output = 'A'
    elif s[-40:]=='35'*20:
        if len(s)<42:
            output = '~B~'
        elif s[-42:-40]!='35':
            output = '~B~'
        else:
            output = 'N'
    elif s[-18:]=='36'*9:
        if len(s)<20:
            output = '~L~'
        elif s[-20:-18]!='36':
            output = '~L~'
        else:
            output = 'E'
    elif s[-40:]=='45'*20:
        if len(s)<42:
            output = '~I~'
        elif s[-42:-40]!='45':
            output = '~I~'
        else:
            output = 'N'
    elif s[-24:]=='46'*12:
        if len(s)<26:
            output = '~N~'
        elif s[-26:-24]!='46':
            output = '~N~'
        else:
            output = 'E'
    elif s[-10:]=='56'*5:
        if len(s)<12:
            output = '~D~'
        elif s[-12:-10]!='56':
            output = '~D~'
        else:
            output = 'E'
    #braille
    elif s[-25:]=='2312452351124523234512456':
        output = '~Hurley~'
    #lost
    elif s[-108:]==('1'*4)+('2'*8)+('3'*15)+('4'*16)+('5'*23)+('6'*42):
        output = 'Your answer is the location of the art gallery known as "The Museum of Insanity"'
    #base
    elif s[-1:]=='1':
        output = 'I'
    elif s[-1:]=='2':
        output = 'N'
    elif s[-1:]=='3':
        output = 'S'
    elif s[-1:]=='4':
        output = 'A'
    elif s[-1:]=='5':
        output = 'N'
    elif s[-1:]=='6':
        output = 'E'

    data = {
        'output': output
        }
    return JsonResponse(data,status = 200)