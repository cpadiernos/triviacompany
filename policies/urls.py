from django.urls import path

from . import views

urlpatterns = [
    path('', views.PolicyListView.as_view(), name='policy-list'),
    path('new/', views.PolicyCreate.as_view(), name='policy-create'),
    path('<int:pk>/update/', views.PolicyUpdate.as_view(), name='policy-update'),
    path('<int:pk>/delete/', views.PolicyDelete.as_view(), name='policy-delete'),
    path('<int:pk>/sections/new/', views.SectionCreate.as_view(), name='section-create'),
    path('<int:policy_pk>/sections/<int:section_pk>/update/', views.SectionUpdate.as_view(), name='section-update'),
    path('<int:policy_pk>/sections/<int:section_pk>/delete/', views.SectionDelete.as_view(), name='section-delete'),
    path('<int:policy_pk>/sections/<int:section_pk>/move/', views.SectionMove.as_view(), name='section-move'),
]