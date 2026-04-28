# accounts/views.py
# Author: Samuel Coelho (w2078214) 
# Group element - signin and signup functionality

# Co-authored: Theoayman Haid De Azevedo (w2116344) 
# Group element - add view request for the forgotpassword and reset pages

from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render, redirect


def signin_view(request):
    """Handle user login - displays form on GET, processes on POST"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('/dashboard/')
    return render(request, 'signin.html')


def signup_view(request):
    """Handle user registration - creates new user account"""
    if request.method == 'POST':
        email = request.POST.get('email')
        username = request.POST.get('username')
        password = request.POST.get('password')
        confirm = request.POST.get('confirm_password')

        if password == confirm and username and email:
            User.objects.create_user(
                username=username,
                email=email,
                password=password
            )
            return redirect('/login/')

    return render(request, 'signup.html')

def forgotpassword_view(request):
    if request.method == "POST":
        email = request.POST.get("email")
        if email:
            return redirect("/reset/")
    return render(request, "forgotpassword.html")

def reset_view(request):
    return render(request, 'reset.html')