from django.urls import path

from . import views

urlpatterns = [
    path('policies/', views.PolicyListView.as_view(), name='policy-list'),
    path('policies/new/', views.PolicyCreate.as_view(), name='policy-create'),
    path('policies/<int:pk>/update/', views.PolicyUpdate.as_view(), name='policy-update'),
    path('policies/<int:pk>/delete/', views.PolicyDelete.as_view(), name='policy-delete'),
    path('policies/<int:pk>/sections/new/', views.SectionCreate.as_view(), name='section-create'),
    path('policies/<int:policy_pk>/sections/<int:section_pk>/update/', views.SectionUpdate.as_view(), name='section-update'),
    path('policies/<int:policy_pk>/sections/<int:section_pk>/delete/', views.SectionDelete.as_view(), name='section-delete'),
    path('policies/<int:policy_pk>/sections/<int:section_pk>/move/', views.SectionMove.as_view(), name='section-move'),
]