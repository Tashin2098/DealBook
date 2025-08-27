from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from .models import StartupProfile

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

        if password1 != password2:
            messages.error(request, "Passwords do not match.")
            return render(request, "signup.html")
        if len(password1) < 8:
            messages.error(request, "Password must be at least 8 characters long.")
            return render(request, "signup.html")
        if User.objects.filter(username=email).exists():
            messages.error(request, "Email already exists.")
            return render(request, "signup.html")

        user = User.objects.create_user(username=email, email=email, password=password1, first_name=name)
        user.save()
        messages.success(request, "Account created successfully. Please sign in.")
        return redirect("login")
    return render(request, "signup.html")

def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email', '').lower()
        password = request.POST.get('password', '')

        user = authenticate(request, username=email, password=password)
        if user is not None:
            login(request, user)
            return redirect('post_login')
        else:
            messages.error(request, "Invalid credentials.")
            return render(request, 'login.html')
    return render(request, 'login.html')

@login_required
def post_login_view(request):
    user = request.user
    if user.is_staff or user.is_superuser:
        return redirect('admin_dashboard')

    # --- THIS IS NEW: Check for StartupProfile
    if hasattr(user, 'startup_profile'):
        # They already completed startup onboarding, show approval page
        return redirect('startup_onboard_complete')
    else:
        # Not completed onboarding, send to onboarding
        return redirect('onboarding')

@staff_member_required
def admin_dashboard(request):
    return render(request, 'admin_dashboard.html')

@login_required
def onboarding_view(request):
    return render(request, 'onboarding.html')

def investor_onboarding(request):
    return render(request, "investor_onboarding_form.html")

# ---------------- ONBOARDING MULTISTEP ----------------

@login_required
def startup_onboard_step1(request):
    fields = [
        'startup_name', 'role', 'email', 'website', 'heard_about', 'description',
        'audience', 'tech_component', 'your_edge', 'pitch_deck_url', 'startup_stage'
    ]
    onboard_data = request.session.get('onboard_data', {})
    if request.method == "POST":
        data = {f: request.POST.get(f, '').strip() for f in fields}
        if any(not data[f] for f in fields):
            messages.error(request, "All fields are required.")
            return render(request, "onboarding_step1.html", {**onboard_data, **data})
        onboard_data.update(data)
        request.session['onboard_data'] = onboard_data
        return redirect('onboard_step2')
    return render(request, "onboarding_step1.html", onboard_data)

@login_required
def startup_onboard_step2(request):
    fields = [
        'problem', 'solution', 'market_research', 'business_model_mind', 'working_time',
        'cofounder', 'support_needed'
    ]
    onboard_data = request.session.get('onboard_data', {})
    if request.method == "POST":
        data = {f: request.POST.get(f, '').strip() for f in fields}
        if any(not data[f] for f in fields):
            messages.error(request, "All fields are required.")
            return render(request, "onboarding_step2.html", {**onboard_data, **data})
        onboard_data.update(data)
        request.session['onboard_data'] = onboard_data
        return redirect('onboard_step3')
    return render(request, "onboarding_step2.html", onboard_data)

@login_required
def startup_onboard_step3(request):
    fields = [
        'has_mvp', 'tested_with_customers', 'funding_source', 'early_users',
        'generated_revenue', 'stage3_challenges', 'stage3_support'
    ]
    onboard_data = request.session.get('onboard_data', {})
    if request.method == "POST":
        data = {f: request.POST.get(f, '').strip() for f in fields}
        if any(not data[f] for f in fields):
            messages.error(request, "All fields are required.")
            return render(request, "onboarding_step3.html", {**onboard_data, **data})
        onboard_data.update(data)
        request.session['onboard_data'] = onboard_data
        return redirect('onboard_step4')
    return render(request, "onboarding_step3.html", onboard_data)

@login_required
def startup_onboard_step4(request):
    fields = [
        'business_model', 'paying_customers', 'annual_revenue_4', 'external_funding',
        'team_size', 'acquisition_strategies', 'stage4_challenges', 'stage4_support'
    ]
    onboard_data = request.session.get('onboard_data', {})
    if request.method == "POST":
        data = {f: request.POST.get(f, '').strip() for f in fields}
        if any(not data[f] for f in fields):
            messages.error(request, "All fields are required.")
            return render(request, "onboarding_step4.html", {**onboard_data, **data})
        onboard_data.update(data)
        request.session['onboard_data'] = onboard_data
        return redirect('onboard_step5')
    return render(request, "onboarding_step4.html", onboard_data)

@login_required
def startup_onboard_step5(request):
    fields = [
        'annual_revenue_5', 'active_customers_5', 'markets_operating', 'expansion_plans', 'stage5_challenges'
    ]
    onboard_data = request.session.get('onboard_data', {})
    if request.method == "POST":
        data = {f: request.POST.get(f, '').strip() for f in fields}
        if any(not data[f] for f in fields):
            messages.error(request, "All fields are required.")
            return render(request, "onboarding_step5.html", {**onboard_data, **data})
        onboard_data.update(data)
        # ----- Save everything to DB here -----
        StartupProfile.objects.update_or_create(
            user=request.user,
            defaults=onboard_data
        )
        request.session['onboard_data'] = onboard_data
        return redirect("startup_onboard_complete")
    return render(request, "onboarding_step5.html", onboard_data)

@login_required
def startup_onboard_complete(request):
    profile = StartupProfile.objects.filter(user=request.user).first()
    is_approved = profile.is_approved if profile else False
    user_name = request.user.first_name
    company_name = profile.startup_name if profile else ""
    context = {
        "is_approved": is_approved,
        "user_name": user_name,
        "company_name": company_name,
    }
    return render(request, "onboarding_complete.html", context)
