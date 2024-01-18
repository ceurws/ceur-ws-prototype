from django.shortcuts import render, redirect
from .models import Workshop, Paper

def index(request):
    return render(request, 'workshops/index.html')

def create_workshop(request):
    # Logic to create a workshop
    return render(request, 'workshops/create_workshop.html')

def submit_paper(request):
    # Logic to submit a paper
    return render(request, 'workshops/submit_paper.html')