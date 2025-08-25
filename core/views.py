from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required

@api_view(['GET'])
def hello_world(request):
    return Response({"message": "Hello, DealBook API!"})

def homepage(request):
    return render(request, 'homepage.html')

def signup_view(request):
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")

        # Password checks
        if password1 != password2:
            messages.error(request, "Passwords do not match.")
            return render(request, "signup.html")
        if len(password1) < 8:
            messages.error(request, "Password must be at least 8 characters long.")
            return render(request, "signup.html")
        if User.objects.filter(username=email).exists():
            messages.error(request, "Email already exists.")
            return render(request, "signup.html")

        # Create user
        user = User.objects.create_user(username=email, email=email, password=password1, first_name=name)
        user.save()
        messages.success(request, "Account created successfully. Please sign in.")
        return redirect("login")  # Make sure your login url is named 'login'

    return render(request, "signup.html")

def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email', '').lower()
        password = request.POST.get('password', '')

        user = authenticate(request, username=email, password=password)
        if user is not None:
            login(request, user)
            return redirect('post_login')  # This will handle admin/user redirect
        else:
            messages.error(request, "Invalid credentials.")
            return render(request, 'login.html')

    return render(request, 'login.html')

@login_required
def post_login_view(request):
    """
    After login/signup, redirect to admin dashboard if admin,
    else redirect to onboarding page for regular users.
    """
    user = request.user
    if user.is_staff or user.is_superuser:
        return redirect('admin_dashboard')
    else:
        return redirect('onboarding')

@staff_member_required
def admin_dashboard(request):
    return render(request, 'admin_dashboard.html')

@login_required
def onboarding_view(request):
    return render(request, 'onboarding.html')
