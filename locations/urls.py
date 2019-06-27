from django.urls import path

from . import views

urlpatterns = [
    path('', views.VenueListView.as_view(), name='venue-list'),
    path('new/', views.VenueCreate.as_view(), name='venue-create'),
    path('<int:pk>/update/', views.VenueUpdate.as_view(), name='venue-update'),
    path('ajax/cities/', views.load_cities, name='city-dropdown-list'),
]