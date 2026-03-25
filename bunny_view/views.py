import base64
import json
import uuid

from django.core.files.base import ContentFile
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from datetime import date
from django.http import HttpResponseRedirect, JsonResponse

from db.models import Rabbit, RabbitImage, RabbitLitter

# Create your views here.
def rabbit_detail(request, pk):
    rabbit = get_object_or_404(Rabbit, pk=pk)
    images = RabbitImage.objects.filter(rabbit_id=rabbit)
    parents = Rabbit.objects.exclude(pk=pk).order_by('name')
    litters = None
    if rabbit.sex == "M":
        litters = RabbitLitter.objects.filter(buck = rabbit)
    elif rabbit.sex == "F":
        litters = RabbitLitter.objects.filter(doe = rabbit)
    
    buck = rabbit.buck
    doe = rabbit.doe

    file_uploader = {
        "widget_id":    "myUpload",
        "label":        "Add Images",
        "hidden_name":  "attachments",
        "hidden_value": "[]",
    }
    return render(request, 'rabbit_detail.html', {'rabbit': rabbit, 'buck': buck, 'doe': doe, 'parents': parents, 'litters':litters, 'images':images, 'image_upload': file_uploader})


def rabbit_edit(request, pk):
    """Handle POST from the detail-page inline edit form to update a rabbit."""
    rabbit = get_object_or_404(Rabbit, pk=pk)

    if request.method != 'POST':
        return redirect('bunny_view:rabbit_detail', pk=pk)

    # basic fields
    name = request.POST.get('name', rabbit.name)
    all_images = json.loads(request.POST.get('attachments'))
    
    # parent (ignore self)
    parent_ids = request.POST.get('parent_ids', '').split(',')
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
                        return redirect('bunny_view:rabbit_detail', pk=pk)
                elif parent.sex == 'F':
                    if not doe:
                        doe = parent
                    else:
                        messages.error(request,
                            'Only one Doe may be selected. Please try again.')
                        return redirect('bunny_view:rabbit_detail', pk=pk)
            except Rabbit.DoesNotExist:
                parent = None

    breed = request.POST.get('breed', rabbit.breed)
    note = request.POST.get('note', rabbit.note)
    temprament = request.POST.get('temprament', rabbit.temprament)

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
    date_of_death = rabbit.date_of_death if dead else None
    dod_str = request.POST.get('date_of_death')
    if dod_str:
        try:
            date_of_death = date.fromisoformat(dod_str)
        except Exception:
            date_of_death = None

    cause_of_death = request.POST.get('cause_of_death', rabbit.cause_of_death)

    # apply updates
    rabbit.name = name or ''
    rabbit.buck=buck
    rabbit.doe=doe
    rabbit.breed = breed
    rabbit.note = note or ''
    rabbit.temprament = temprament or ''
    rabbit.date_of_birth = dob
    rabbit.sex = sex or ''
    rabbit.dead = dead
    rabbit.date_of_death = date_of_death
    rabbit.cause_of_death = cause_of_death or ''
    rabbit.save()

    if len(all_images) != 0:
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

    messages.success(request, 'Updated rabbit: {}'.format(rabbit))
    return redirect('bunny_view:rabbit_detail', pk=pk)

def rabbit_delete(request, pk):
    rabbit = get_object_or_404(Rabbit, pk=pk)
    if rabbit.image.name != "rabbits/Default.png":
        rabbit.image.delete()
    rabbit.delete()
    return redirect(request.session.get('previous_page'))

def rabbit_crop(request, pk):
    rabbit_crop = request.FILES.get("cropped_image")
    rabbit = get_object_or_404(Rabbit, pk=pk)
    parents = Rabbit.objects.exclude(pk=pk).order_by('name')
    
    cropped = RabbitImage.objects.create(
        rabbit_id=rabbit,
        image=rabbit_crop
    )
    rabbit_model = Rabbit.objects.get(pk = pk)
    rabbit_model.image = cropped.image
    rabbit_model.save()
    litters = None
    if rabbit.sex == "M":
        litters = RabbitLitter.objects.filter(buck = rabbit).order_by("litter_number")
    elif rabbit.sex == "F":
        litters = RabbitLitter.objects.filter(doe = rabbit).order_by("litter_number")
    
    images = RabbitImage.objects.filter(rabbit_id=rabbit)

    return render(request, 'rabbit_detail.html', {'rabbit': rabbit, 'buck': rabbit.buck, 'doe':rabbit.doe, 'parents': parents, 'litters':litters, 'images':images})

def rabbit_default(request, pk):
    image_id = request.POST.get("image_id")
    image = get_object_or_404(RabbitImage,image_id=image_id)
    rabbit = get_object_or_404(Rabbit,pk=pk)
    rabbit.image = image.image
    rabbit.save()
    return JsonResponse({'rabbit_image': rabbit.image.url})

def rabbit_image_delete(request, pk):
    image_id = request.POST.get("image_id")
    image = get_object_or_404(RabbitImage,image_id=image_id)
    image.delete()
    return JsonResponse({'rabbit_image': image_id})
