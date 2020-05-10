from django.urls import path
from . import views
from users import views as user_views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.home, name='hunt20-home'),
    path('invalid/', views.invalid, name='hunt20-invalid'),
    path('faq/', views.faq, name='hunt20-faq'),
    path('about/', views.about, name='hunt20-about'),
    path('guide/', views.guide, name='hunt20-guide'),
    
    path('puzzles/', views.puzzles, name='hunt20-puzzles'),
    path('puzzles/<str:puzzle_id>/', views.puzzle_archives, name='hunt20-puzzle-archives'),
    path('puzzles/<str:puzzle_id>/submit/', views.submit, name='hunt20-submit'),
    path('puzzles/<str:puzzle_id>/solution/', views.solution_archives, name='hunt20-solution-archives'),

    path('register/', user_views.register, name='hunt20-register'),
    path('login/', auth_views.LoginView.as_view(template_name='users/login.html'), name="hunt20-login"),
    path('logout/', auth_views.LogoutView.as_view(template_name='users/logout.html'), name="hunt20-logout"),
]