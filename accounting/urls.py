from django.urls import path

from . import views

urlpatterns = [
    path('pay-stubs/<int:pk>/', views.PayStubDetailView.as_view(),
        name='pay-stub-detail'),
    path('pay-stubs/<str:username>/', views.PayStubListViewUser.as_view(),
        name='pay-stub-list-user'),
    path('pay-stubs/<str:username>/current/', views.PayStubListViewCurrentUser.as_view(),
        name='pay-stub-list-current-user'),
    path('pay-stubs/<str:username>/past/', views.PayStubListViewPastUser.as_view(),
        name='pay-stub-list-past-user'),
    path('reimbursements/new/', views.ReimbursementCreateView.as_view(),
        name='reimbursement-create'),
    path('reimbursements/<str:username>/', views.ReimbursementListViewUser.as_view(),
        name='reimbursement-list-user'),
    path('reimbursements/<int:pk>/update/', views.ReimbursementUpdateView.as_view(),
        name='reimbursement-update'),
    ]