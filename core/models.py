from django.db import models
from django.contrib.auth.models import User


class StartupProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='startup_profile')

    # --- Step 1 ---
    startup_name = models.CharField(max_length=150)
    role = models.CharField(max_length=100)
    email = models.EmailField()
    website = models.CharField(max_length=255)
    heard_about = models.CharField(max_length=50)
    description = models.TextField()
    audience = models.TextField()
    tech_component = models.TextField()
    your_edge = models.TextField()
    pitch_deck_url = models.CharField(max_length=255)
    startup_stage = models.CharField(max_length=50)

    # --- Step 2 ---
    problem = models.TextField()
    solution = models.TextField()
    market_research = models.CharField(max_length=20)
    business_model_mind = models.CharField(max_length=50)
    working_time = models.CharField(max_length=50)
    cofounder = models.CharField(max_length=20)
    support_needed = models.TextField()

    # --- Step 3 ---
    has_mvp = models.CharField(max_length=10)
    tested_with_customers = models.CharField(max_length=10)
    funding_source = models.CharField(max_length=100)
    early_users = models.CharField(max_length=10)
    generated_revenue = models.CharField(max_length=20)
    stage3_challenges = models.TextField()
    stage3_support = models.TextField()

    # --- Step 4 ---
    business_model = models.TextField()
    paying_customers = models.CharField(max_length=50)
    annual_revenue_4 = models.CharField(max_length=50)
    external_funding = models.CharField(max_length=50)
    acquisition_strategies = models.TextField()
    team_size = models.CharField(max_length=50)
    stage4_challenges = models.TextField()
    stage4_support = models.TextField()

    # --- Step 5 ---
    annual_revenue_5 = models.CharField(max_length=50)
    active_customers_5 = models.CharField(max_length=50)
    markets_operating = models.CharField(max_length=100)
    expansion_plans = models.TextField()
    stage5_challenges = models.TextField()

    # --- Approval / Admin ---
    is_approved = models.BooleanField(default=False)
    is_onboarded = models.BooleanField(default=False)
    submitted_at = models.DateTimeField(auto_now_add=True)



    def __str__(self):
        return f"{self.user.username} — {self.startup_name}"



class InvestorProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='investor_profile')

    # --- Investor Onboarding Fields ---
    company = models.CharField(max_length=150, blank=True, null=True)
    linkedin = models.URLField(max_length=255, blank=True, null=True)

    hear_about = models.CharField(max_length=50)   # Social Media, Referral, etc.
    experience = models.CharField(max_length=50)  # Angel, VC, Corporate, etc.
    industries = models.CharField(max_length=255) # Comma separated industries

    investment_range = models.CharField(max_length=50)  # Below 50k, 50k-100k etc.
    looking_for = models.JSONField(default=list, blank=True)  # Stores multiple checkbox values

    newsletter = models.CharField(max_length=10, choices=[("yes", "Yes"), ("no", "No")])
    comments = models.TextField(blank=True, null=True)

    # --- Approval / Admin ---
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)



    def __str__(self):
        return f"Investor: {self.investment_range} ({self.looking_for})"