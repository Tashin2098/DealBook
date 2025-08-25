from django.shortcuts import render

# Create your views here.
from rest_framework.decorators import api_view
from rest_framework.response import Response

@api_view(['GET'])
def hello_world(request):
    return Response({"message": "Hello, DealBook API!"})
def homepage(request):
    return render(request, 'homepage.html')
def login_view(request):
    return render(request, 'login.html')
