from django.shortcuts import render
from .views import *
# Create your views here.
app_name='Quote'

def home(request):
    return render(request,'Quote/index.html')