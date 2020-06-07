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