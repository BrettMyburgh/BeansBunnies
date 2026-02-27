from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.template.loader import render_to_string
from datetime import date, timedelta
from db.models import Rabbit


def home(request):
    rabbits = Rabbit.objects.all()
    
    adults_rabbit = rabbits.filter(date_of_birth__lt=date.today() - timedelta(days=14*7))
    juvenile_rabbit = rabbits.filter(date_of_birth__lt=date.today() - timedelta(days=8*7), date_of_birth__gte=date.today()-timedelta(days=14*7))
    kits_rabbit = rabbits.filter(date_of_birth__gte=date.today() - timedelta(days=8*7))
    deceased_rabbit = rabbits.filter(date_of_death__isnull=False)
    
    categories = {"adults":adults_rabbit, "juvenile":juvenile_rabbit, "kits":kits_rabbit, "deceased":deceased_rabbit}

    if request.method == 'POST':
        name = request.POST.get('name')
        image = request.FILES.get('image')
        parent_ids = request.POST.get('parent_ids').split(',')
        Buck = None
        Doe = None
        for i in range(len(parent_ids)):
            parent_ids[i] = parent_ids[i].strip()
            parent = None
            if parent_ids[i].isdigit():
                try:
                    parent = Rabbit.objects.get(pk=parent_ids[i])
                    if parent.sex == 'M':
                        if not Buck:
                            Buck = parent
                        else:
                            messages.error(request,
                                'Only one Buck may be selected. Please try again.')
                            return redirect('home')
                    elif parent.sex == 'F':
                        if not Doe:
                            Doe = parent
                        else:
                            messages.error(request,
                                'Only one Doe may be selected. Please try again.')
                            return redirect('home')
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
            buck=Buck,
            doe=Doe,
            breed=breed,
            date_of_birth=dob,
            sex=sex,
        )

        messages.success(request, 'Saved rabbit: {}'.format(rabbit))
        return redirect('home')

    return render(request, 'home.html', {'groups': categories, 'parents': rabbits})


def categories_ajax(request):
    sex = request.GET.get('sex', '')
    rabbits = Rabbit.objects.all()
    if sex:
        rabbits = rabbits.filter(sex=sex)

    adults_rabbit = rabbits.filter(date_of_birth__lt=date.today() - timedelta(days=14*7))
    juvenile_rabbit = rabbits.filter(date_of_birth__lt=date.today() - timedelta(days=8*7), date_of_birth__gte=date.today()-timedelta(days=14*7))
    kits_rabbit = rabbits.filter(date_of_birth__gte=date.today() - timedelta(days=8*7))
    deceased_rabbit = rabbits.filter(date_of_death__isnull=False)

    categories = {"adults":adults_rabbit, "juvenile":juvenile_rabbit, "kits":kits_rabbit, "deceased":deceased_rabbit}

    html = render_to_string('home/_rabbit_cards.html', {'groups': categories, 'sex': sex}, request=request)
    return JsonResponse({'html': html})


