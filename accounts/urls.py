from django.urls import path

from . import views

urlpatterns = [
    path('hosts/', views.HostProfileListView.as_view(), name='host-profile-list'),
    path('accounts/<str:username>/', views.CustomUserUpdate.as_view(), name='account-update'),
]