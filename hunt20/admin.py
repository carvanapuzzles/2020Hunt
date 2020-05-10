from django.contrib import admin
from .models import Puzzle
from .models import Team
from .models import Submission

admin.site.register(Puzzle)
admin.site.register(Team)
admin.site.register(Submission)
