import re
from django.shortcuts import render
from django.http import HttpResponse

def home(request):
    context = {}
    return render(request, 'hunt20/home.html', context)

def puzzles(request):
    context = {}
    return render(request, 'hunt20/puzzles.html', context)

def puzzle_archives(request, puzzle_id):
    context = {}
    puzzle_html = 'hunt20/puzzles/' + puzzle_id + '.html'
    return render(request, puzzle_html, context)
