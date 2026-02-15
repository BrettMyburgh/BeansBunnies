from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('rabbit/<int:pk>/', views.rabbit_detail, name='rabbit_detail'),
    path('deceased/', views.deceased_list, name='deceased'),
]