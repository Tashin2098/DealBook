from django.urls import path
from .views import hello_world, homepage, login_view, signup_view, post_login_view, admin_dashboard, onboarding_view

urlpatterns = [
    path('hello/', hello_world),
    path('', homepage, name='homepage'),
    path('signup/', signup_view, name='signup'),

    path('login/', login_view, name='login'),
    
    path('post-login/', post_login_view, name='post_login'),
    path('admin-dashboard/', admin_dashboard, name='admin_dashboard'),
    path('onboarding/', onboarding_view, name='onboarding'),
]
