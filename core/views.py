from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.admin.views.decorators import staff_member_required
from .models import StartupProfile, InvestorProfile, InvestorCompanySave, InvestorInvestment, StartupDocument
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.shortcuts import render, redirect, get_object_or_404
from collections import Counter
from .models import StartupProfile,InvestorProfile, CapTableEntry


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

    if hasattr(user, 'startup_profile'):
        profile = user.startup_profile
        if not profile.is_approved:
            # Awaiting admin approval after 1st form
            return redirect('startup_onboard_complete')

        # Approved but not onboarded yet
        if profile.is_approved and not profile.is_onboarded:
            if not profile.complete_profile_submitted:
                # Show 2nd profile form (step 1)
                return redirect('startup_complete_profile_step1')
            else:
                # 2nd form submitted, awaiting admin to onboard
                return redirect('startup_onboard_pending')

        # Approved AND onboarded (all done)
        if profile.is_onboarded:
            return redirect('startup_dashboard')

    # --- Check for Investor Onboarding ---
    if hasattr(user, 'investor_profile'):
        return redirect('investor_onboard_complete')

    # Not completed onboarding, send to onboarding
    return redirect('onboarding')

@staff_member_required
def admin_dashboard(request):
    return render(request, 'admin_dashboard.html')
@user_passes_test(lambda u: u.is_staff or u.is_superuser)
def admin_users_view(request):
    users = User.objects.all().order_by('-date_joined')
    if request.headers.get("HX-Request") == "true":
        # return only the content (no sidebar)
        return render(request, "admin_partials/admin_users_partial.html", {"users": users})
    else:
        # return full page with sidebar
        return render(request, "admin_users.html", {"users": users})

@staff_member_required
def startup_users_admin(request):
    startups = StartupProfile.objects.all().select_related('user').order_by('-submitted_at')
    if request.headers.get("HX-Request") == "true":
        # return only the content (no sidebar)
        return render(request, "admin_partials/admin_startup_users_partial.html", {"startups": startups})
    else:
        # return full page with sidebar
        return render(request, 'admin_startup_users.html', {
        'startups': startups
    })

@require_POST
@staff_member_required
def toggle_startup_status(request):
    import json
    data = json.loads(request.body)
    sid = data.get("id")
    field = data.get("field")
    value = data.get("value")
    # Parse value to bool (if checkbox, comes as string 'true'/'false')
    value = value in ['true', 'True', True, 1, '1']
    if field not in ["is_approved", "is_onboarded"]:
        return JsonResponse({"success": False, "error": "Invalid field"}, status=400)
    try:
        startup = StartupProfile.objects.get(pk=sid)
        setattr(startup, field, value)
        # Logic: Disapproving also disables onboarded
        if field == "is_approved" and not value:
            startup.is_onboarded = False
        startup.save()
        return JsonResponse({"success": True})
    except StartupProfile.DoesNotExist:
        return JsonResponse({"success": False, "error": "Not found"}, status=404)

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
    is_onboarded = profile.is_onboarded if profile else False
    user_name = request.user.first_name
    company_name = profile.startup_name if profile else ""
    context = {
        "is_approved": is_approved,
        "is_onboarded": is_onboarded,
        "user_name": user_name,
        "company_name": company_name,
    }
    return render(request, "onboarding_complete.html", context)

# ------------------- COMPLETE PROFILE: PHASE 2 FOR STARTUP -------------------
@login_required
def startup_complete_profile_step1(request):
    # Phase 2 Step 1: First 6 questions (ARR, ARPU, Burn, Cash, LTV:CAC, OpEx, Debt)
    if not hasattr(request.user, 'startup_profile'):
        return redirect('onboarding')
    profile = request.user.startup_profile
    if not profile.is_approved:
        return redirect('startup_onboard_complete')
    # If already onboarded, skip
    if profile.is_onboarded:
        return redirect('startup_dashboard')  # replace with dashboard

    if request.method == "POST":
        arr = request.POST.get('arr')
        arpu = request.POST.get('arpu')
        monthly_burn = request.POST.get('monthly_burn')
        cash_balance = request.POST.get('cash_balance')
        ltv_cac_ratio = request.POST.get('ltv_cac_ratio')
        operating_expenses = request.POST.get('operating_expenses')
        debt_obligations = request.POST.get('debt_obligations')

        # Store in session for step2
        request.session['profile_step1'] = {
            "arr": arr, "arpu": arpu, "monthly_burn": monthly_burn,
            "cash_balance": cash_balance, "ltv_cac_ratio": ltv_cac_ratio,
            "operating_expenses": operating_expenses, "debt_obligations": debt_obligations
        }
        return redirect('startup_complete_profile_step2')

    # Prefill if session data exists
    data = request.session.get('profile_step1', {})
    return render(request, "startup_complete_profile_step1.html", data)

@login_required
def startup_complete_profile_step2(request):
    # Phase 2 Step 2: Rest of the questions (Capital, Raising, Equity, Forecast)
    if not hasattr(request.user, 'startup_profile'):
        return redirect('onboarding')
    profile = request.user.startup_profile
    if not profile.is_approved:
        return redirect('startup_onboard_complete')
    if profile.is_onboarded:
        return redirect('startup_dashboard')  # replace with dashboard

    if request.method == "POST":
        capital_raised = request.POST.get('capital_raised')
        currently_raising = request.POST.get('currently_raising')
        equity_offered = request.POST.get('equity_offered')
        financial_forecast = request.FILES.get('financial_forecast')

        # Get previous answers from step1
        prev = request.session.get('profile_step1', {})
        # Update profile fields
        profile.arr = prev.get('arr')
        profile.arpu = prev.get('arpu')
        profile.monthly_burn = prev.get('monthly_burn')
        profile.cash_balance = prev.get('cash_balance')
        profile.ltv_cac_ratio = prev.get('ltv_cac_ratio')
        profile.operating_expenses = prev.get('operating_expenses')
        profile.debt_obligations = prev.get('debt_obligations')
        profile.capital_raised = capital_raised
        profile.currently_raising = currently_raising
        profile.equity_offered = equity_offered
        if financial_forecast:
            profile.financial_forecast = financial_forecast
        profile.complete_profile_submitted = True
        profile.save()
        # Remove session data
        if 'profile_step1' in request.session:
            del request.session['profile_step1']
        return redirect('startup_onboard_pending')  # replace with dashboard

    return render(request, "startup_complete_profile_step2.html")

# ---------------- INVESTOR ONBOARDING FORM ----------------
@login_required
def investor_onboard(request):
    fields = [
        'company', 'linkedin',
        'hear_about', 'experience', 'industries',
        'investment_range', 'newsletter', 'comments'
    ]

    onboard_data = request.session.get('investor_data', {})

    if request.method == "POST":
        data = {f: request.POST.get(f, '').strip() for f in fields}

        # Handle checkboxes (lookingFor[] in HTML)
        looking_for = request.POST.getlist('lookingFor')
        data['looking_for'] = looking_for

        # Validation: required fields
        required_fields = ['hear_about', 'experience', 'industries', 'investment_range', 'newsletter']
        if any(not data.get(f) for f in required_fields):
            messages.error(request, "Please fill all required fields.")
            return render(request, "investor_onboarding_form.html", {**onboard_data, **data})

        # Save to session
        onboard_data.update(data)
        request.session['investor_data'] = onboard_data

        # Save to DB (create or update profile)
        InvestorProfile.objects.update_or_create(
            user=request.user,
            defaults=onboard_data
        )


        return redirect("investor_onboard_complete")

    return render(request, "investor_onboarding_form.html", onboard_data)

@login_required
def investor_onboard_complete(request):
    profile = InvestorProfile.objects.filter(user=request.user).first()
    is_approved = profile.is_approved if profile else False
    user_name = request.user.first_name

    if is_approved:
        # If approved, redirect to dashboard
        return redirect("investor_dashboard")

    # Otherwise show submitted/pending page
    context = {
        "is_approved": is_approved,
        "user_name": user_name,
    }
    return render(request, "investor_onboarding_complete.html", context)


@staff_member_required
def investor_users_admin(request):
    investors = InvestorProfile.objects.all().select_related('user').order_by('-created_at')
    if request.headers.get("HX-Request") == "true":
        # return only the content (no sidebar)
        return render(request, "admin_partials/admin_investor_users_partial.html", {"investors": investors})
    else:
        # return full page with sidebar
        return render(request, 'admin_investor_users.html', {
        'investors': investors
    }) 


@require_POST
@staff_member_required
def toggle_investor_status(request):
    import json
    data = json.loads(request.body)
    iid = data.get("id")
    field = data.get("field")
    value = data.get("value")
    # Parse value to bool (for checkbox)
    value = value in ['true', 'True', True, 1, '1']
    if field not in ["is_approved"]:
        return JsonResponse({"success": False, "error": "Invalid field"}, status=400)
    try:
        investor = InvestorProfile.objects.get(pk=iid)
        setattr(investor, field, value)
        investor.save()
        return JsonResponse({"success": True})
    except InvestorProfile.DoesNotExist:
        return JsonResponse({"success": False, "error": "Not found"}, status=404)
    
@login_required
def startup_onboard_pending(request):
    return render(request, "startup_onboard_pending.html")

@login_required
def startup_dashboard(request):
    # You can add your real dashboard logic later
    return render(request, "startup_dashboard.html")


@login_required
def startup_dashboard(request):
    profile = getattr(request.user, 'startup_profile', None)
    if not profile or not profile.is_onboarded:
        return redirect('post_login')  # Handle edge cases (not onboarded, etc.)

    # Prepare widget/stat data
    widget_data = {
        "ARR": profile.arr or 0,
        "ARPU": profile.arpu or 0,
        "Burn": profile.monthly_burn or 0,
        "Cash": profile.cash_balance or 0,
        "LTV_CAC": profile.ltv_cac_ratio or 0,
        "Currently Raising": profile.currently_raising or 0,
        "Equity Offered": profile.equity_offered or 0,
        "Approval": "✅ Approved" if profile.is_approved else "⏳ Pending",
        "Onboarded": "✅" if profile.is_onboarded else "⏳",
    }

    # Example activity list (customize as needed)
    activities = [
        {"date": profile.submitted_at, "desc": "Profile submitted"},
        {"date": profile.submitted_at, "desc": "Profile approved by admin"} if profile.is_approved else None,
        {"date": profile.submitted_at, "desc": "Completed onboarding"} if profile.is_onboarded else None,
        # You can add more activity from fundraise, etc.
    ]
    # Filter out None values
    activities = [a for a in activities if a]

    return render(request, "startup_dashboard.html", {
        "widget_data": widget_data,
        "activities": activities,
        "profile": profile,
        "section": "dashboard"
    })

@login_required
def startup_company_overview(request):
    profile = request.user.startup_profile
    if request.headers.get("HX-Request") == "true":
        # return only the content (no sidebar)
        return render(request, "startup_partials/startup_company_overview_partial.html", {"profile": profile})
    else:
        # return full page with sidebar
        return render(request, "startup_company_overview.html", {"profile": profile})
    

@login_required
def startup_edit_overview(request):
    profile = request.user.startup_profile
    if request.method == "POST":
        profile.startup_name = request.POST.get('startup_name', profile.startup_name)
        profile.website = request.POST.get('website', profile.website)
        profile.role = request.POST.get('role', profile.role)
        profile.startup_stage = request.POST.get('startup_stage', profile.startup_stage)
        profile.audience = request.POST.get('audience', profile.audience)
        profile.tech_component = request.POST.get('tech_component', profile.tech_component)
        profile.your_edge = request.POST.get('your_edge', profile.your_edge)
        profile.description = request.POST.get('description', profile.description)
        profile.save()
        messages.success(request, "Company overview updated.")
        return redirect("startup_company_overview")
    return render(request, "startup_edit_overview.html", {"profile": profile})


@login_required
def startup_financial_metrics(request):
    profile = request.user.startup_profile
    if request.headers.get("HX-Request") == "true":
        # return only the content (no sidebar)
        return render(request, "startup_partials/startup_financial_metrics_partial.html", {"profile": profile})
    else:
        # return full page with sidebar
        return render(request, "startup_financial_metrics.html", {"profile": profile})
    

@login_required
def startup_edit_financial_metrics(request):
    profile = request.user.startup_profile
    if request.method == "POST":
        profile.arr = request.POST.get('arr', profile.arr)
        profile.arpu = request.POST.get('arpu', profile.arpu)
        profile.monthly_burn = request.POST.get('monthly_burn', profile.monthly_burn)
        profile.cash_balance = request.POST.get('cash_balance', profile.cash_balance)
        profile.ltv_cac_ratio = request.POST.get('ltv_cac_ratio', profile.ltv_cac_ratio)
        profile.operating_expenses = request.POST.get('operating_expenses', profile.operating_expenses)
        profile.save()
        messages.success(request, "Financial metrics updated.")
        return redirect("startup_financial_metrics")
    return render(request, "startup_financial_metrics.html", {"profile": profile})

@login_required
def startup_fundraising_status(request):
    profile = request.user.startup_profile
    if request.headers.get("HX-Request") == "true":
        # return only the content (no sidebar)
        return render(request, "startup_partials/startup_fundraising_status_partial.html", {"profile": profile})
    else:
        # return full page with sidebar
        return render(request, "startup_fundraising_status.html", {"profile": profile})
    

@login_required
def startup_edit_fundraising_status(request):
    profile = request.user.startup_profile
    if request.method == "POST":
        profile.currently_raising = request.POST.get('currently_raising', profile.currently_raising)
        profile.equity_offered = request.POST.get('equity_offered', profile.equity_offered)
        profile.capital_raised = request.POST.get('capital_raised', profile.capital_raised)
        profile.debt_obligations = request.POST.get('debt_obligations', profile.debt_obligations)
        profile.external_funding = request.POST.get('external_funding', profile.external_funding)
        profile.save()
        messages.success(request, "Fundraising status updated.")
        return redirect("startup_fundraising_status")
    return render(request, "startup_fundraising_status.html", {"profile": profile})

@login_required
def startup_my_fundraise(request):
    profile = request.user.startup_profile
    context = {
        'currently_raising': profile.currently_raising,
        'equity_offered': profile.equity_offered,
        'capital_raised': profile.capital_raised,
        'pitch_deck_url': profile.pitch_deck_url,
    }

    if request.headers.get("HX-Request") == "true":
        # return only the content (no sidebar)
        return render(request, "startup_partials/startup_my_fundraise_partial.html", context)
    else:
        # return full page with sidebar
        return render(request, "startup_my_fundraise.html", context)
    

@login_required
def startup_investor_outreach(request):
    # For now, mock empty outreach; can be extended to database table later
    outreach_list = []  # Example: [{'name': 'John Doe', 'firm': 'VC Firm', ...}]
    if request.headers.get("HX-Request") == "true":
        # return only the content (no sidebar)
        return render(request, "startup_partials/startup_investor_outreach_partial.html", {'outreach_list': outreach_list})
    else:
        # return full page with sidebar
        return render(request, "startup_investor_outreach.html", {'outreach_list': outreach_list})
    

@login_required
def startup_fundraising_dashboard(request):
    profile = request.user.startup_profile
    # In future: load fundraising chart data, now just show main stats
    context = {
        'currently_raising': profile.currently_raising,
        'capital_raised': profile.capital_raised,
        'equity_offered': profile.equity_offered,
    }
    if request.headers.get("HX-Request") == "true":
        # return only the content (no sidebar)
        return render(request, "startup_partials/startup_fundraising_dashboard_partial.html", context)
    else:
        # return full page with sidebar
        return render(request, "startup_fundraising_dashboard.html", context)
    

@login_required
def startup_round_history(request):
    profile = request.user.startup_profile
    # In future: loop through multiple rounds. For now, show current.
    rounds = [{
        'type': 'Current',
        'capital_raised': profile.capital_raised,
        'equity_offered': profile.equity_offered,
        'start_date': profile.submitted_at,
        'pitch_deck_url': profile.pitch_deck_url,
    }]

    if request.headers.get("HX-Request") == "true":
        # return only the content (no sidebar)
        return render(request, "startup_partials/startup_round_history_partial.html", {'rounds': rounds})
    else:
        # return full page with sidebar
        return render(request, "startup_round_history.html", {'rounds': rounds})
    

@login_required
def startup_valuation_financials(request):
    profile = request.user.startup_profile
    if request.headers.get("HX-Request") == "true":
        # return only the content (no sidebar)
        return render(request, "startup_partials/startup_valuation_financials_partial.html", {"profile": profile})
    else:
        # return full page with sidebar
        return render(request, "startup_valuation_financials.html", {"profile": profile})
    

@login_required
def startup_cap_table(request):
    # Get the logged-in startup's cap table
    startup_profile = request.user.startup_profile
    cap_entries = CapTableEntry.objects.filter(startup=startup_profile)

    # For demo, if empty, generate fake data (remove in production)
    if not cap_entries.exists():
        cap_entries = [
            {'name': 'Founder 1', 'shares': 4000, 'percent': 40},
            {'name': 'Founder 2', 'shares': 4000, 'percent': 40},
            {'name': 'Employee Pool', 'shares': 1000, 'percent': 10},
            {'name': 'Investor A', 'shares': 1000, 'percent': 10},
        ]
        context = {'cap_table': cap_entries}
    else:
        context = {
            'cap_table': [
                {'name': entry.name, 'shares': entry.shares, 'percent': entry.percent}
                for entry in cap_entries
            ]
        }

    if request.headers.get("HX-Request") == "true":
        # return only the content (no sidebar)
        return render(request, "startup_partials/startup_cap_table_partial.html", context)
    else:
        # return full page with sidebar
        return render(request, 'startup_cap_table.html', context)
    
@login_required
def investor_dashboard(request):
    investor_profile = getattr(request.user, 'investor_profile', None)
    if not investor_profile:
        return redirect('investor_onboarding')

    investments = InvestorInvestment.objects.filter(investor=investor_profile)
    saved_count = InvestorCompanySave.objects.filter(investor=request.user).count()  # If still FK to User
    # If you also updated InvestorCompanySave to use InvestorProfile:
    # saved_count = InvestorCompanySave.objects.filter(investor=investor_profile).count()

    return render(request, "investor_dashboard.html", {
        "section": "dashboard",
        "investments": investments,
        "saved_count": saved_count
    })

@login_required
def investor_company_overview(request):
    profile = getattr(request.user, 'investor_profile', None)
    return render(request, "investor_company_overview.html", {
        "profile": profile,
        "section": "company"
    })

# ---------------- Deal Discovery ----------------
@login_required
def browse_companies(request):
    # Get InvestorProfile object for this user (required for InvestorInvestment)
    investor_profile = getattr(request.user, 'investor_profile', None)
    startups = StartupProfile.objects.filter(is_onboarded=True)

    # For saves: filter with User (request.user)
    saved = set(
        InvestorCompanySave.objects.filter(investor=request.user)
        .values_list('startup_id', flat=True)
    )

    # For investments: filter with InvestorProfile
    invested = set()
    if investor_profile:
        invested = set(
            InvestorInvestment.objects.filter(investor=investor_profile)
            .values_list('startup_id', flat=True)
        )

    return render(request, "browse_companies.html", {
        "section": "deal_discovery",
        "subsection": "browse_companies",
        "startups": startups,
        "saved": saved,
        "invested": invested,
    })



@login_required
def save_company(request, startup_id):
    startup = get_object_or_404(StartupProfile, pk=startup_id)
    InvestorCompanySave.objects.get_or_create(investor=request.user, startup=startup)
    return redirect('browse_companies')

@login_required
def saved_companies(request):
    saves = InvestorCompanySave.objects.filter(investor=request.user).select_related('startup')
    return render(request, "saved_companies.html", {
        "section": "deal_discovery",
        "subsection": "saved_companies",
        "saves": saves
    })

@login_required
def invest_in_company(request, startup_id):
    investor_profile = getattr(request.user, 'investor_profile', None)
    if not investor_profile:
        # Optional: Show error or redirect to onboarding
        return redirect('investor_onboarding')

    startup = get_object_or_404(StartupProfile, pk=startup_id)

    if request.method == "POST":
        amount = request.POST.get("amount")
        equity = request.POST.get("equity")
        notes = request.POST.get("notes")
        # Add any other form values you want to save!

        # Create the investment
        InvestorInvestment.objects.create(
            investor=investor_profile,
            startup=startup,
            amount=amount or None,
            equity=equity or None,
            notes=notes or "",
            status="pending"
        )
        messages.success(request, "Investment successfully recorded!")
        return redirect('browse_companies')

    context = {
        "startup": startup,
        "default_equity": startup.equity_offered,        # from model
        "default_investment": startup.currently_raising,
        "default_users": 70000,
        "default_conversion": 39,
        "default_avg_txn": 100,
        "default_roi_display": "yearly",
    }
    return render(request, "invest_in_company.html", context)


@login_required
def investment_pipeline(request):
    # Show investments where is_active=True (not completed)
    investor_profile = getattr(request.user, 'investor_profile', None)
    if not investor_profile:
        return redirect('investor_onboarding')
    pipeline = InvestorInvestment.objects.filter(
        investor=investor_profile,
        is_active=True
    ).select_related('startup').order_by('-invested_at')
    return render(request, "investment_pipeline.html", {
        "pipeline": pipeline,
        "section": "deal_discovery",
        "subsection": "investment_pipeline"
    })

@login_required
def sector_analysis(request):
    investor_profile = getattr(request.user, 'investor_profile', None)
    # All startups invested in:
    invested_ids = InvestorInvestment.objects.filter(investor=investor_profile).values_list('startup_id', flat=True)
    saved_ids = InvestorCompanySave.objects.filter(investor=request.user).values_list('startup_id', flat=True)
    all_startup_ids = list(invested_ids) + list(saved_ids)
    startups = StartupProfile.objects.filter(id__in=all_startup_ids)
    sectors = [s.tech_component or "Unknown" for s in startups]  # Change to your actual field!
    sector_counts = dict(Counter(sectors))
    return render(request, "sector_analysis.html", {
        "sector_counts": sector_counts,
        "section": "deal_discovery",
        "subsection": "sector_analysis"
    })

# ----------- Investment Management ------------
@login_required
def active_investments(request):
    investor_profile = getattr(request.user, 'investor_profile', None)
    if not investor_profile:
        # Optionally redirect to onboarding or error
        return redirect('investor_onboarding')

    investments = InvestorInvestment.objects.filter(
        investor=investor_profile,
        is_active=True,
        status__in=['pending', 'approved']
    ).select_related('startup').order_by('-invested_at')
    return render(request, "active_investments.html", {
        "investments": investments,
        "section": "investment_management",
        "subsection": "active_investments",
    })

@login_required
def investments_history(request):
    investor_profile = getattr(request.user, 'investor_profile', None)
    if not investor_profile:
        return redirect('investor_onboarding')

    investments = InvestorInvestment.objects.filter(
        investor=investor_profile
    ).select_related('startup').order_by('-invested_at')
    return render(request, "investments_history.html", {
        "investments": investments,
        "section": "investment_management",
        "subsection": "investments_history",
    })

@login_required
def analytics_dashboard(request):
    investor_profile = getattr(request.user, 'investor_profile', None)
    investments = InvestorInvestment.objects.filter(investor=investor_profile)
    total_invested = sum(inv.amount or 0 for inv in investments)
    total_roi = sum(((inv.startup.arr or 0) * (inv.startup.equity_offered or 0)/100) for inv in investments)  # Example calc
    num_investments = investments.count()
    top_startups = investments.order_by('-amount')[:3]
    return render(request, "analytics_dashboard.html", {
        "total_invested": total_invested,
        "total_roi": total_roi,
        "num_investments": num_investments,
        "top_startups": top_startups,
        "section": "portfolio_analytics",
        "subsection": "analytics_dashboard"
    })

@login_required
def my_data_room(request):
    investor_profile = getattr(request.user, 'investor_profile', None)
    invested_ids = InvestorInvestment.objects.filter(investor=investor_profile).values_list('startup_id', flat=True)
    saved_ids = InvestorCompanySave.objects.filter(investor=request.user).values_list('startup_id', flat=True)
    all_startup_ids = list(invested_ids) + list(saved_ids)
    docs = StartupDocument.objects.filter(startup__id__in=all_startup_ids).select_related('startup').order_by('-uploaded_at')
    return render(request, "my_data_room.html", {
        "docs": docs,
        "section": "data_room_access",
        "subsection": "my_data_room"
    })
