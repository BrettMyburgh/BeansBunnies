from django.urls import path
from . import views

app_name = 'bunny_view'

urlpatterns = [
    path('rabbit/<int:pk>/', views.rabbit_detail, name='rabbit_detail'),
    path('rabbit/<int:pk>/edit/', views.rabbit_edit, name='rabbit_edit'),
    path('rabbit/<int:pk>/delete/', views.rabbit_delete, name='rabbit_delete'),
    path('rabbit/<int:pk>/crop/', views.rabbit_crop, name='rabbit_crop'),
]