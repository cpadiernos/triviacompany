from django.conf import settings
from django.urls import path

from . import views

urlpatterns = [
    path('game-supplies/', views.GameListView.as_view(),
        name='game-list'),
    path('{}/<path:path>'.format(settings.PRIVATE_STORAGE_URL[1:-1]),
        views.login_required_private_file, name='login-required-private-file'),
    ]