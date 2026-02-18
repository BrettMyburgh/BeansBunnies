from django.shortcuts import render
from .models import Rabbit

# Create your views here.
def group_view(request):
    parents = Rabbit.objects.all()

    return render(request, 'group_view/group_view.html', {'parents': parents})