from django.urls import path

from . import views

urlpatterns = [
    path('venues/', views.VenueListView.as_view(), name='venue-list'),
    path('venues/new/', views.VenueCreate.as_view(), name='venue-create'),
    path('venues/<int:pk>/update/', views.VenueUpdate.as_view(), name='venue-update'),
    path('venues/ajax/cities/', views.load_cities, name='city-dropdown-list'),
]