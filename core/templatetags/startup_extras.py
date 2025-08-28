import json
from django import template

register = template.Library()

@register.filter
def as_json(obj):
    fields = [
        "startup_name", "role", "email", "heard_about", "description", "audience",
        "tech_component", "your_edge", "pitch_deck_url", "startup_stage", "problem", "solution",
        "market_research", "business_model_mind", "working_time", "cofounder", "support_needed",
        "has_mvp", "tested_with_customers", "funding_source", "early_users", "generated_revenue",
        "stage3_challenges", "stage3_support", "business_model", "paying_customers",
        "annual_revenue_4", "external_funding", "team_size", "acquisition_strategies",
        "stage4_challenges", "stage4_support", "annual_revenue_5", "active_customers_5",
        "markets_operating", "expansion_plans", "stage5_challenges"
    ]
    data = {}
    for f in fields:
        data[f] = getattr(obj, f, "")

    # Only add string fields from user
    data['user_first_name'] = getattr(obj.user, 'first_name', '')
    data['user_email'] = getattr(obj.user, 'email', '')

    return json.dumps(data)
