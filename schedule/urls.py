from django.urls import path

from . import views

urlpatterns = [
    path('', views.EventOccurrenceListView.as_view(
            template_name = 'schedule/event_occurrence_list_with_filter.html'),
        name='event-occurrence-list'),
    path('<int:pk>/', views.EventDetailView.as_view(),
        name='event-detail'),
    path('<int:pk>/update/', views.EventOccurrenceUpdate.as_view(),
        name='event-occurrence-update'),
    path('<int:pk>/request-off/', views.RequestOff.as_view(),
        name='request-off'),
    path('<int:pk>/pick-up/', views.PickUp.as_view(),
        name='pick-up'),
    path('available/', views.EventOccurrenceListViewAvailable.as_view(),
        name='event-occurrence-list-available'),
    path('<str:username>/all/', views.EventOccurrenceListViewHost.as_view(),
        name='event-occurrence-list-host'),
    path('<str:username>/past/', views.EventOccurrenceListViewPastHost.as_view(),
        name='event-occurrence-list-past-host'),
    path('<str:username>/future/', views.EventOccurrenceListViewFutureHost.as_view(),
        name='event-occurrence-list-future-host'),
    ]