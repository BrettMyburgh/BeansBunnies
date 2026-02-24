from datetime import date, timedelta
from django.shortcuts import render
from db.models import Rabbit # type: ignore

# Create your views here.
def group_view(request, category, filter=''):
    rabbits = Rabbit.objects.all()
    parents = rabbits
    if filter != 'A':
        rabbits = rabbits.filter(sex=filter or filter == '')

    match category:
        case 'adults':
            rabbits = rabbits.filter(date_of_birth__lt=date.today() - timedelta(days=14*7))
        case 'juvenile':
            rabbits = rabbits.filter(date_of_birth__lt=date.today() - timedelta(days=8*7), date_of_birth__gte=date.today()-timedelta(days=14*7))
        case 'kits':
            rabbits = rabbits.filter(date_of_birth__gte=date.today() - timedelta(days=8*7))
        case 'deceased':
            rabbits = rabbits.filter(date_of_death__isnull=False)
    return render(request, 'group_view.html', {'rabbits': rabbits, 'parents': parents, 'sex': filter})