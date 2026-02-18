from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from datetime import date

from db.models import Rabbit

# Create your views here.
def rabbit_detail(request, pk):
    rabbit = get_object_or_404(Rabbit, pk=pk)
    parents = Rabbit.objects.exclude(pk=pk).order_by('name')
    return render(request, 'rabbit_detail.html', {'rabbit': rabbit, 'parents': parents})


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
