from django import template

register = template.Library()

@register.simple_tag
def has_solved_puzzle(team, puzzle_id):
    return team.has_solved_puzzle(puzzle_id)

@register.simple_tag
def hints_taken_on_puzzle(team, puzzle_name):
    return team.hints_taken_on_puzzle(puzzle_name)
    
@register.simple_tag
def incorrect_answers_on_puzzle(team, puzzle_id):
    return team.incorrect_answers_on_puzzle(puzzle_id)