from django.urls import path

from . import views

urlpatterns = [
    path('', views.HostProfileListView.as_view(), name='host-profile-list'),
]