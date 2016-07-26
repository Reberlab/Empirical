__author__ = 'drlemur'

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

def index(request):
    return render(request,'index.html')

@login_required
def home(request):
    return redirect('study_index')
    #return render(request,'home.html')
