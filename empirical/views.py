__author__ = 'Paul J. Reber'

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from exp.models import Study

def index(request):
    # Collect list of available studies
    study_list = Study.objects.filter(homepage_visible=True)
    link_list=[]
    for i in study_list:
        link_list.append(i.current_experiment.link_url(request))
    return render(request,'index.html', {'studies': zip(study_list, link_list)})

@login_required
def home(request):
    return redirect('study_index')
    #return render(request,'home.html')
