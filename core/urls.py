from django.urls import path
from .views import hello_world, homepage, login_view, signup_view, post_login_view, admin_dashboard, onboarding_view, investor_onboarding, startup_onboard_step1, startup_onboard_step2, startup_onboard_step3, startup_onboard_step4, startup_onboard_step5, startup_onboard_complete, admin_users_view, startup_users_admin, toggle_startup_status, startup_complete_profile_step1, startup_complete_profile_step2, startup_onboard_pending, startup_dashboard, startup_company_overview, startup_edit_overview, startup_financial_metrics, startup_edit_financial_metrics, startup_fundraising_status, startup_edit_fundraising_status, startup_my_fundraise, startup_investor_outreach, startup_fundraising_dashboard, startup_round_history, startup_cap_table, startup_valuation_financials, investor_users_admin, toggle_investor_status
from django.contrib.auth import views as auth_views
from .views import hello_world, homepage, login_view, signup_view, post_login_view, admin_dashboard, onboarding_view, investor_onboarding,investor_onboard,investor_onboard_complete, startup_onboard_step1, startup_onboard_step2, startup_onboard_step3, startup_onboard_step4, startup_onboard_step5, startup_onboard_complete


urlpatterns = [
    path('hello/', hello_world),
    path('', homepage, name='homepage'),
    path('signup/', signup_view, name='signup'),

    path('login/', login_view, name='login'),
    
    path('post-login/', post_login_view, name='post_login'),
    path('admin-dashboard/', admin_dashboard, name='admin_dashboard'),
    path('onboarding/', onboarding_view, name='onboarding'),
    path("onboarding/investor/", investor_onboarding, name="investor_onboarding"),
    path("onboarding/investor/onboard/", investor_onboard, name="investor_onboard"),
    path("onboarding/investor/complete/", investor_onboard_complete, name="investor_onboard_complete"),

    path('onboarding/startup/step1/', startup_onboard_step1, name='onboard_step1'),
    path('onboarding/startup/step2/', startup_onboard_step2, name='onboard_step2'),
    path('onboarding/startup/step3/', startup_onboard_step3, name='onboard_step3'),
    path('onboarding/startup/step4/', startup_onboard_step4, name='onboard_step4'),
    path('onboarding/startup/step5/', startup_onboard_step5, name='onboard_step5'),
    path("onboarding/startup/complete/", startup_onboard_complete, name="startup_onboard_complete"),
    path('admin-dashboard/users/', admin_users_view, name='admin_users'),
    path('admin-dashboard/startup-users/', startup_users_admin, name='startup_users'),
    path("admin-dashboard/toggle-status/", toggle_startup_status, name="toggle_startup_status"),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('startup/complete-profile/step1/', startup_complete_profile_step1, name='startup_complete_profile_step1'),
    path('startup/complete-profile/step2/', startup_complete_profile_step2, name='startup_complete_profile_step2'),
    path("startup/complete-profile/pending/", startup_onboard_pending, name="startup_onboard_pending"),
    path('startup/dashboard/', startup_dashboard, name='startup_dashboard'),
    path('startup/company-overview/', startup_company_overview, name='startup_company_overview'),
    path('startup/company-overview/edit/', startup_edit_overview, name='startup_edit_overview'),
    path('startup/financial-metrics/', startup_financial_metrics, name='startup_financial_metrics'),
    path('startup/financial-metrics/edit/', startup_edit_financial_metrics, name='startup_edit_financial_metrics'),
    path('startup/fundraising-status/', startup_fundraising_status, name='startup_fundraising_status'),
    path('startup/fundraising-status/edit/', startup_edit_fundraising_status, name='startup_edit_fundraising_status'),
    path('startup/valuation-financials/', startup_valuation_financials, name='startup_valuation_financials'),
    path('startup/fundraising/my-fundraise/', startup_my_fundraise, name='startup_my_fundraise'),
    path('startup/fundraising/investor-outreach/', startup_investor_outreach, name='startup_investor_outreach'),
    path('startup/fundraising/dashboard/', startup_fundraising_dashboard, name='startup_fundraising_dashboard'),
    path('startup/fundraising/round-history/', startup_round_history, name='startup_round_history'),
    path('startup/cap-table/', startup_cap_table, name='startup_cap_table'),
     path('admin-dashboard/investor-users/', investor_users_admin, name='investor_users'),
    path('admin-dashboard/toggle-investor-status/', toggle_investor_status, name='toggle_investor_status'),



]
