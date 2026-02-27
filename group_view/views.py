from datetime import date, timedelta
from django.shortcuts import render, redirect
from django.contrib import messages
from db.models import Rabbit # type: ignore

# Create your views here.
def group_view(request, category, filter=''):
    rabbits = Rabbit.objects.all()
    parents = rabbits
    if filter != 'A':
        rabbits = rabbits.filter(sex=filter or filter == '')

    if request.method == 'POST':
        name = request.POST.get('name')
        image = request.FILES.get('image')
        parent_ids = request.POST.get('parent_ids').split(',')
        buck = None
        doe = None
        for i in range(len(parent_ids)):
            parent_ids[i] = parent_ids[i].strip()
            parent = None
            if parent_ids[i].isdigit():
                try:
                    parent = Rabbit.objects.get(pk=parent_ids[i])
                    if parent.sex == 'M':
                        if not buck:
                            buck = parent
                        else:
                            messages.error(request,
                                'Only one Buck may be selected. Please try again.')
                            return redirect(request.path)
                    elif parent.sex == 'F':
                        if not doe:
                            doe = parent
                        else:
                            messages.error(request,
                                'Only one Doe may be selected. Please try again.')
                            return redirect(request.path)
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
            buck=buck,
            doe=doe,
            breed=breed,
            date_of_birth=dob,
            sex=sex,
        )

        messages.success(request, 'Saved rabbit: {}'.format(rabbit))
        return redirect(request.path)
    
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