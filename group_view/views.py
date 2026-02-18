from django.shortcuts import render
from db.models import Rabbit # type: ignore

# Create your views here.
def group_view(request):
    parents = Rabbit.objects.all()

    return render(request, 'group_view/group_view.html', {'parents': parents})