# teams/urls.py
# Author: Samuel Coelho (w2078214)
from django.urls import path
from . import views

urlpatterns = [
    path('', views.team_list, name='team_list'),
    path('<int:team_id>/', views.team_detail, name='team_detail'),
]