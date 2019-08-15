from django.urls import path

from . import views

urlpatterns = [
    path('events/', views.EventOccurrenceListView.as_view(
            template_name = 'schedule/event_occurrence_list_with_filter.html'),
        name='event-occurrence-list'),
    path('event-details/<int:pk>/', views.EventDetailView.as_view(),
        name='event-detail'),
    path('events/<int:pk>/update/', views.EventOccurrenceUpdate.as_view(),
        name='event-occurrence-update'),
    path('events/<int:pk>/', views.EventOccurrenceDetail.as_view(),
        name='event-occurrence-detail'),
    path('events/<int:pk>/request-off/', views.RequestOff.as_view(),
        name='request-off'),
    path('events/<int:pk>/pick-up/', views.PickUp.as_view(),
        name='pick-up'),
    path('events/available/', views.EventOccurrenceListViewAvailable.as_view(),
        name='event-occurrence-list-available'),
    path('events/<str:username>/all/', views.EventOccurrenceListViewHost.as_view(),
        name='event-occurrence-list-host'),
    path('events/<str:username>/past/', views.EventOccurrenceListViewPastHost.as_view(),
        name='event-occurrence-list-past-host'),
    path('events/<str:username>/future/', views.EventOccurrenceListViewFutureHost.as_view(),
        name='event-occurrence-list-future-host'),
    path('events/ajax/days/', views.load_days, name='day-dropdown-list'),
    ]