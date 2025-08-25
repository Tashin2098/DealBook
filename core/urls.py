from django.urls import path
from .views import hello_world, homepage, login_view, signup_view

urlpatterns = [
    path('hello/', hello_world),
    path('', homepage, name='homepage'),
    path('signup/', signup_view, name='signup'),

    path('login/', login_view, name='login'),
]
