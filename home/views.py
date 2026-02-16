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
    parents = Rabbit.objects.exclude(pk=pk).order_by('name')
    return render(request, 'home/rabbit_detail.html', {'rabbit': rabbit, 'parents': parents})


def rabbit_edit(request, pk):
    """Handle POST from the detail-page modal to update a rabbit."""
    rabbit = get_object_or_404(Rabbit, pk=pk)

    if request.method != 'POST':
        return redirect('rabbit_detail', pk=pk)

    # basic fields
    name = request.POST.get('name', rabbit.name)
    image = request.FILES.get('image')

    # parent (ignore self)
    parent = None
    parent_id = request.POST.get('parent')
    if parent_id:
        try:
            parent_obj = Rabbit.objects.get(pk=parent_id)
            if parent_obj.pk != rabbit.pk:
                parent = parent_obj
        except Rabbit.DoesNotExist:
            parent = None

    breed = request.POST.get('breed', rabbit.breed)

    dob = rabbit.date_of_birth
    dob_str = request.POST.get('date_of_birth')
    if dob_str:
        try:
            dob = date.fromisoformat(dob_str)
        except Exception:
            dob = None

    sex = request.POST.get('sex', rabbit.sex)

    # death fields
    dead = bool(request.POST.get('dead'))
    date_of_death = rabbit.date_of_death
    dod_str = request.POST.get('date_of_death')
    if dod_str:
        try:
            date_of_death = date.fromisoformat(dod_str)
        except Exception:
            date_of_death = None

    cause_of_death = request.POST.get('cause_of_death', rabbit.cause_of_death)

    # apply updates
    rabbit.name = name or ''
    if image:
        rabbit.image = image
    rabbit.parent = parent
    rabbit.breed = breed
    rabbit.date_of_birth = dob
    rabbit.sex = sex or ''
    rabbit.dead = dead
    rabbit.date_of_death = date_of_death
    rabbit.cause_of_death = cause_of_death or ''
    rabbit.save()

    messages.success(request, 'Updated rabbit: {}'.format(rabbit))
    return redirect('rabbit_detail', pk=pk)


def deceased_list(request):
    """List all rabbits marked as dead with their reason/date of death."""
    dead_rabbits = Rabbit.objects.filter(dead=True).order_by('-date_of_death', '-created')
    return render(request, 'home/deceased.html', {'dead_rabbits': dead_rabbits})