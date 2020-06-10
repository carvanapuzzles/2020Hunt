from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class Puzzle(models.Model):
    puzzle_id = models.CharField(max_length=100)
    puzzle_name = models.CharField(max_length=100)
    puzzle_ans = models.CharField(max_length=100)
    puzzle_midpoint = models.CharField(max_length=100, default="DNE")
    puzzle_cluephrase = models.CharField(max_length=100 , default="DNE")
    unlocks_at = models.IntegerField(default=0)
    in_round = models.IntegerField(default=1)
    objects = models.Manager()

    def __str__(self):
        return self.puzzle_name

    @property
    def puzzle_solves(self):
        super_users = User.objects.filter(is_superuser=True).values_list('username',flat=True)
        test_solvers = User.objects.filter(team__is_testsolver=True).values_list('username',flat=True)
        return Submission.objects.filter(puzzle_id=self.puzzle_id).filter(correct=True).exclude(username__in=super_users).exclude(username__in=test_solvers).count()

    @property
    def puzzle_submissions(self):
        super_users = User.objects.filter(is_superuser=True).values_list('username',flat=True)
        test_solvers = User.objects.filter(team__is_testsolver=True).values_list('username',flat=True)
        return Submission.objects.filter(puzzle_id=self.puzzle_id).exclude(username__in=super_users).exclude(username__in=test_solvers).count()
    
    @property
    def unique_teams(self):
        return Submission.objects.filter(puzzle_id=self.puzzle_id).values_list('username').distinct().count()
    
    @property
    def get_abbr(self):
        return str(self.puzzle_name).replace(" ","")[:5]
    
class Team(models.Model):
    username = models.OneToOneField(User, on_delete=models.CASCADE, null=True)
    created_datetime = models.DateTimeField(default=timezone.now)
    name = models.CharField(max_length=400)
    is_testsolver = models.BooleanField(default=False)
    captain = models.CharField(max_length=100, default='DNE')
    member1 = models.CharField(max_length=100, default='DNE')
    member2 = models.CharField(max_length=100, default='DNE')
    member3 = models.CharField(max_length=100, default='DNE')
    member4 = models.CharField(max_length=100, default='DNE')
    member5 = models.CharField(max_length=100, default='DNE')
    objects = models.Manager()

    def __str__(self):
        return self.name
    
    @property
    def get_list_of_solves(self):
        return Submission.objects.filter(username=self.username).filter(correct=True)
    
    @property
    def total_solves(self):
        return Submission.objects.filter(username=self.username).filter(correct=True).count()

    def round_solves(self, round_number):
        return Submission.objects.filter(username=self.username).filter(correct=True).filter(puzzle__in_round=round_number).count()
    
    @property
    def last_solve_datetime(self):
        correct_subs = Submission.objects.filter(username=self.username).filter(correct=True)
        if correct_subs.exists():
            return correct_subs.latest('eventdatetime').eventdatetime
        else:
            return self.created_datetime

    @property
    def in_round(self):
        if Submission.objects.filter(username=self.username).filter(correct=True).filter(puzzle__puzzle_id='p06').exists():
            if Submission.objects.filter(username=self.username).filter(correct=True).filter(puzzle__puzzle_id='p13').exists():
                rd = 3
            else:
                rd = 2
        else:
            rd = 1
        return rd
            

    @property
    def hints_remaining(self):
        hints_taken = HintRequest.objects.filter(username=self.username).filter(refunded=False).count()
        return 10 - hints_taken
    
    def has_solved_puzzle(self, puzzle_id):
        return Submission.objects.filter(username=self.username).filter(correct=True).filter(puzzle__puzzle_id=puzzle_id).exists()

    def hints_taken_on_puzzle(self, puzzle_name):
        return HintRequest.objects.filter(username=self.username).filter(puzzle_name=puzzle_name).filter(refunded=False).count()
    
    def incorrect_answers_on_puzzle(self, puzzle_id):
        return Submission.objects.filter(username=self.username).filter(correct=False).filter(puzzle__puzzle_id=puzzle_id).count()

@receiver(post_save, sender=User)
def create_team(sender, instance, created, **kwargs):
    if created:
        Team.objects.create(username=instance)

@receiver(post_save, sender=User)
def save_team(sender, instance, **kwargs):
    instance.team.save()

class Submission(models.Model):
    username = models.CharField(max_length=100)
    puzzle = models.ForeignKey(Puzzle, on_delete=models.CASCADE, default=1)
    team_ans = models.CharField(max_length=100)
    eventdatetime = models.DateTimeField()
    correct = models.BooleanField()
    objects = models.Manager()

    def __str__(self):
        if self.correct:
            outcome = 'correct'
        else:
            outcome = 'incorrect'
        return '_'.join([self.username, self.puzzle.puzzle_id, self.team_ans, outcome])

class HintRequest(models.Model):
    username = models.CharField(max_length=100)
    puzzle_name = models.CharField(max_length=100)
    team_question = models.TextField()
    hq_ans = models.TextField(default="(pending...)")
    eventdatetime = models.DateTimeField()
    answered = models.BooleanField()
    refunded = models.BooleanField(default=False)
    objects = models.Manager()

    def __str__(self):
        if self.answered:
            status = 'closed'
        else:
            status = 'open'
        return '_'.join([self.username, self.puzzle_name, status])        
