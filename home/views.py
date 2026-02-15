from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from datetime import date

from .models import Rabbit


def home(request):
    parents = Rabbit.objects.all()

    if request.method == 'POST':
        name = request.POST.get('name')
        image = request.FILES.get('image')
        parent_id = request.POST.get('parent')
        parent = None
        if parent_id:
            try:
                parent = Rabbit.objects.get(pk=parent_id)
            except Rabbit.DoesNotExist:
                parent = None

        breed = request.POST.get('breed', '')
        dob_str = request.POST.get('date_of_birth')
        dob = None
        if dob_str:
            try:
                dob = date.fromisoformat(dob_str)
            except Exception:
                dob = None

        sex = request.POST.get('sex', '')

        rabbit = Rabbit.objects.create(
            name=name or '',
            image=image,
            parent=parent,
            breed=breed,
            date_of_birth=dob,
            sex=sex,
        )

        messages.success(request, 'Saved rabbit: {}'.format(rabbit))
        return redirect('home')

    return render(request, 'home/home.html', {'parents': parents})


def rabbit_detail(request, pk):
    rabbit = get_object_or_404(Rabbit, pk=pk)
    return render(request, 'home/rabbit_detail.html', {'rabbit': rabbit})


def deceased_list(request):
    """List all rabbits marked as dead with their reason/date of death."""
    dead_rabbits = Rabbit.objects.filter(dead=True).order_by('-date_of_death', '-created')
    return render(request, 'home/deceased.html', {'dead_rabbits': dead_rabbits})