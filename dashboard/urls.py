# Author: Theoayman Haid De Azevedo
# Individual element - wrote the code

from django.urls import path
from .views import dashboard_view, dashboard_search

urlpatterns = [
    path('', dashboard_view, name='dashboard'),
    path('search/', dashboard_search, name='dashboard_search'),
]