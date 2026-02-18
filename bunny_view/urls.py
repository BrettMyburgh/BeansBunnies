from django.urls import path
from . import views

app_name = 'bunny_view'

urlpatterns = [
    path('rabbit/<int:pk>/', views.rabbit_detail, name='rabbit_detail'),
    path('rabbit/<int:pk>/edit/', views.rabbit_edit, name='rabbit_edit'),
]