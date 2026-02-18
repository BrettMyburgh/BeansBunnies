from django.urls import path
from . import views

urlpatterns = [
    path('deceased/', views.deceased_list, name='deceased'),
]