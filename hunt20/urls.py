from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='hunt20-home'),
    path('puzzles/', views.puzzles, name='hunt20-puzzles'),
    path('puzzles/<str:puzzle_id>/', views.puzzle_archives, name='hunt20-puzzle-archives')
]