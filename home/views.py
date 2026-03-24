from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.template.loader import render_to_string
from datetime import date, timedelta
from django.core.files import File
from django.conf import settings
from django.core.files.base import ContentFile
import base64
import uuid
import json
from db.models import Rabbit, RabbitImage


def home(request):
    rabbits = Rabbit.objects.all()
    
    adults_rabbit = rabbits.filter(date_of_birth__lt=date.today() - timedelta(days=14*7))
    juvenile_rabbit = rabbits.filter(date_of_birth__lt=date.today() - timedelta(days=8*7), date_of_birth__gte=date.today()-timedelta(days=14*7))
    kits_rabbit = rabbits.filter(date_of_birth__gte=date.today() - timedelta(days=8*7))
    undated_rabbit = rabbits.filter(date_of_birth__isnull=True)
    deceased_rabbit = rabbits.filter(date_of_death__isnull=False)
    
    categories = {"Adults":adults_rabbit, "Juvenile":juvenile_rabbit, "Kits":kits_rabbit, "Undated":undated_rabbit, "Deceased":deceased_rabbit}

    list_categories = []
    if(adults_rabbit != None):
        list_categories.append("Adults")
    if(juvenile_rabbit != None):
        list_categories.append("Juvenile")
    if(kits_rabbit != None):
        list_categories.append("Kits")
    if(undated_rabbit != None):
        list_categories.append("Undated")
    if(deceased_rabbit != None):
        list_categories.append("Deceased")

    request.session["categories"] = list_categories
    request.session.modified = True

    if request.method == 'POST':
        name = request.POST.get('name')
        # image = request.FILES.get('image')
        all_images = json.loads(request.POST.get('attachments'))
                
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
                            return redirect('home')
                    elif parent.sex == 'F':
                        if not doe:
                            doe = parent
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

        if len(all_images) == 0:
            rabbit = Rabbit.objects.create(
                name=name or '',
                buck=buck,
                doe=doe,
                breed=breed,
                date_of_birth=dob,
                sex=sex,
            )
        else:
            if ';base64,' in all_images[0]:
                format_str, imgstr = all_images[0].split(';base64,')
                ext = format_str.split('/')[-1]
            else:
                imgstr = all_images[0]
                ext = 'png'
            data = ContentFile(base64.b64decode(imgstr),f"{uuid.uuid4()}.{ext}")
                        
            rabbit = Rabbit.objects.create(
                name=name or '',
                image=data,
                buck=buck,
                doe=doe,
                breed=breed,
                date_of_birth=dob,
                sex=sex,
            )
            for image in all_images:
                if ';base64,' in image:
                    format_str, imgstr = image.split(';base64,')
                    ext = format_str.split('/')[-1]
                else:
                    imgstr = image
                    ext = 'png'
                data = ContentFile(base64.b64decode(imgstr),f"{uuid.uuid4()}.{ext}")
                image = RabbitImage.objects.create(
                    rabbit_id=rabbit,
                    image=data
                )
        messages.success(request, 'Saved rabbit: {}'.format(rabbit))
        return redirect('home')
    
    file_uploader = {
        "widget_id":    "myUpload",
        "label":        "Images",
        "hidden_name":  "attachments",
        "hidden_value": "[]",
    }

    return render(request, 'home.html', {'groups': categories, 'parents': rabbits, 'image_upload': file_uploader})


def categories_ajax(request):
    sex = request.GET.get('sex', '')
    rabbits = Rabbit.objects.all()
    if sex:
        rabbits = rabbits.filter(sex=sex)

    adults_rabbit = rabbits.filter(date_of_birth__lt=date.today() - timedelta(days=14*7))
    juvenile_rabbit = rabbits.filter(date_of_birth__lt=date.today() - timedelta(days=8*7), date_of_birth__gte=date.today()-timedelta(days=14*7))
    kits_rabbit = rabbits.filter(date_of_birth__gte=date.today() - timedelta(days=8*7))
    undated_rabbit = rabbits.filter(date_of_birth__isnull=True)
    deceased_rabbit = rabbits.filter(date_of_death__isnull=False)

    categories = {"Adults":adults_rabbit, "Juvenile":juvenile_rabbit, "Kits":kits_rabbit, "Undated":undated_rabbit, "Deceased":deceased_rabbit}

    if sex == '':
        sex = 'A'

    html = render_to_string('home/_rabbit_cards.html', {'groups': categories, 'sex': sex}, request=request)
    return JsonResponse({'html': html})


