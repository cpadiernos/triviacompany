import datetime
import os

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.views import generic
from django.views.static import serve

from .models import Game

class GameListView(LoginRequiredMixin, generic.ListView):
    model = Game
    template_name = 'questions/game_list.html'

    def get_context_data(self, **kwargs):
        context = super(GameListView, self).get_context_data(**kwargs)
        now = datetime.datetime.now()
        context['game_list_future'] = Game.objects.filter(date__gte=now).order_by('date')
        return context

@login_required
def login_required_private_file(request, path):
    full_path = os.path.join(settings.PRIVATE_STORAGE_ROOT, path)
    if not os.path.isfile(full_path):
        raise Http404
    return serve(request, path, settings.PRIVATE_STORAGE_ROOT)