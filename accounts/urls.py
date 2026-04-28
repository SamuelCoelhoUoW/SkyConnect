# accounts/urls.py
#Co-authored: Samuel Coelho - signin and signup, Theoayman Haid De Azevedo - forgotpassword and reset view
from django.urls import path
from .views import signin_view, signup_view, forgotpassword_view, reset_view

urlpatterns = [
    path('signin/', signin_view, name='signin'),
    path('signup/', signup_view, name='signup'),
    path('forgotpassword/' ,forgotpassword_view, name='forgotpassword'),
    path('reset/', reset_view, name='reset'),
]