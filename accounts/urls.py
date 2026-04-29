# accounts/urls.py
#Co-authored: Samuel Coelho - login and signup, Theoayman Haid De Azevedo - forgotpassword and reset view
from django.urls import path
from .views import login_view, signup_view, forgotpassword_view, reset_view, logout_view

urlpatterns = [
    path('login/', login_view, name='login'),
    path('signup/', signup_view, name='signup'),
    path('forgotpassword/' ,forgotpassword_view, name='forgotpassword'),
    path('reset/', reset_view, name='reset'),
    path("logout/", logout_view, name="logout"),
]