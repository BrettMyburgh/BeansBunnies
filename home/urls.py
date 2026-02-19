from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('ajax/categories/', views.categories_ajax, name='categories_ajax'),
]