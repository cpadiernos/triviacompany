from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.urls import reverse

def home(request):
    return redirect('event-occurrence-list')

def about(request):
    return render(request, 'about.html')

def how_to_play(request):
    return render(request, 'how_to_play.html')

@login_required()
def portal_redirect(request):
    if request.user.is_host:
        return redirect(
            reverse(
                'event-occurrence-list-host',
                kwargs={'username': request.user.username}))
    else:
        return redirect('event-occurrence-list')