# accounts/urls.py
from django.urls import path
from .views import signin_view, signup_view, forgotpassword_view, reset_view

urlpatterns = [
    path('signin/', signin_view, name='login'),
    path('signup/', signup_view, name='signup'),
    path('forgotpassword/' ,forgotpassword_view, name='forgotpassword'),
    path('reset/', reset_view, name='reset'),
]