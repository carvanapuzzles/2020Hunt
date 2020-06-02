from django.contrib import admin
from .models import Puzzle
from .models import Team
from .models import Submission
from .models import HintRequest

admin.site.register(Puzzle)
admin.site.register(Team)
admin.site.register(Submission)
admin.site.register(HintRequest)
