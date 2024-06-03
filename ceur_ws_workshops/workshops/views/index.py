from django.shortcuts import render

def index(request):
    """
    Renders the home page of the workshop site.
    """
    return render(request, 'workshops/index.html')