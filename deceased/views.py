from django.shortcuts import render
from db.models import Rabbit

def deceased_list(request):
    """List all rabbits marked as dead with their reason/date of death."""
    dead_rabbits = Rabbit.objects.filter(dead=True).order_by('-date_of_death', '-created')
    return render(request, 'home/deceased.html', {'dead_rabbits': dead_rabbits})