from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from transactions import views

urlpatterns = [
    path('transaction/', views.TransactionList.as_view(), name='transaction-list-post'),
    path('transaction/<str:pk>/', views.TransactionDetail.as_view(), name='transaction-detail'),
    path('types/<str:type>/', views.TransactionTypeView.as_view(), name='transaction-type'),
    path('sum/<str:pk>/', views.TransactionSum.as_view(), name='transaction-sum'),
]

urlpatterns = format_suffix_patterns(urlpatterns)