from django.urls import path
from . import views

app_name = 'bunny_view'

urlpatterns = [
    path('rabbit/<int:pk>/', views.rabbit_detail, name='rabbit_detail'),
    path('rabbit/<int:pk>/edit/', views.rabbit_edit, name='rabbit_edit'),
    path('rabbit/<int:pk>/delete/', views.rabbit_delete, name='rabbit_delete'),
    path('rabbit/<int:pk>/crop/', views.rabbit_crop, name='rabbit_crop'),
    path('rabbit/<int:pk>/default/', views.rabbit_default, name='rabbit_default'),
    path('rabbit/<int:pk>/image-delete/', views.rabbit_image_delete, name='rabbit_image_delete'),
    path('rabbit/<int:pk>/abandon/', views.rabbit_abandon, name='rabbit_abandon'),
    path('rabbit/<int:pk>/weight/', views.rabbit_weight, name='rabbit_weight'),
    path('rabbit/<int:pk>/feed/', views.rabbit_feed, name='rabbit_feed'),
]