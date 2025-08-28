from django.urls import path
from .views import hello_world, homepage, login_view, signup_view, post_login_view, admin_dashboard, onboarding_view, investor_onboarding, startup_onboard_step1, startup_onboard_step2, startup_onboard_step3, startup_onboard_step4, startup_onboard_step5, startup_onboard_complete, admin_users_view, startup_users_admin, toggle_startup_status
from django.contrib.auth import views as auth_views
urlpatterns = [
    path('hello/', hello_world),
    path('', homepage, name='homepage'),
    path('signup/', signup_view, name='signup'),

    path('login/', login_view, name='login'),
    
    path('post-login/', post_login_view, name='post_login'),
    path('admin-dashboard/', admin_dashboard, name='admin_dashboard'),
    path('onboarding/', onboarding_view, name='onboarding'),
    path("onboarding/investor/", investor_onboarding, name="investor_onboarding"),

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



]
