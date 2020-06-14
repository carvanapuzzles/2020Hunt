from django.utils import timezone
import datetime
import pytz

def get_background(request):
    if request.user.is_authenticated:
        if request.user.team.in_round == 2:
            background = 'snowflake'
        elif request.user.team.in_round == 3:
            background = 'northpole'
        else:
            background = 'puzzlympics'
    else:
        background = 'puzzlympics'
    return background

HUNT_START = pytz.timezone("MST").localize(datetime.datetime(2020, 6, 13, 18, 20))
HUNT_END = pytz.timezone("MST").localize(datetime.datetime(2020, 7, 2, 12, 0))

def get_hunt_status():
    if timezone.now()<HUNT_START:
        return "pre"
    elif timezone.now()<HUNT_END:
        return "active"
    else:
        return "post"

HINTS_4 = pytz.timezone("MST").localize(datetime.datetime(2019, 6, 26, 20, 0))
HINTS_6 = pytz.timezone("MST").localize(datetime.datetime(2019, 8, 26, 20, 0))
HINTS_8 = pytz.timezone("MST").localize(datetime.datetime(2019, 8, 26, 20, 0))
HINTS_10 = pytz.timezone("MST").localize(datetime.datetime(2019, 8, 26, 20, 0))
HINTS_12 = pytz.timezone("MST").localize(datetime.datetime(2019, 8, 26, 20, 0))
HINTS_14 = pytz.timezone("MST").localize(datetime.datetime(2019, 8, 26, 20, 0))


def get_avail_hints():
    if timezone.now()<HINTS_4:
        return 2
    elif timezone.now()<HINTS_6:
        return 4
    elif timezone.now()<HINTS_8:
        return 6
    elif timezone.now()<HINTS_10:
        return 8
    elif timezone.now()<HINTS_12:
        return 10
    elif timezone.now()<HINTS_14:
        return 12
    else:
        return 14
