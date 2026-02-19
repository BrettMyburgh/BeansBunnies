from django.urls import path
from . import views

app_name = 'group_view'

urlpatterns = [
    path('<str:category>/<str:sex>/', views.group_view, name='group_view'),
]