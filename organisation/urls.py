# Author: Ar-rahim Mozumdar w2063830

from django.urls import path
from . import views

urlpatterns = [
    path('', views.organisation_view, name='organisation'),
    path('data/', views.organisation_data_json, name='organisation_data'),
]
