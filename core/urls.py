from django.urls import path
from .views import hello_world, homepage, login_view

urlpatterns = [
    path('hello/', hello_world),
    path('', homepage, name='homepage'),
    path('login/', login_view, name='login'),
]
