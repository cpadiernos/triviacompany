from django.shortcuts import render

def about(request):
    return render(request, 'about.html')

def how_to_play(request):
    return render(request, 'how_to_play.html')