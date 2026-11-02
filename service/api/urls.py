from django.urls import path

from . import views

urlpatterns = [
    path('', views.ServiceListCreateView.as_view(), name='api_service_list'),
    path('<str:pk>/', views.ServiceDetailView.as_view(), name='api_service_detail'),
]
