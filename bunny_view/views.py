import base64
import json
import uuid

from django.core.files.base import ContentFile
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from datetime import date, timedelta
from django.http import HttpResponseRedirect, JsonResponse

from db.models import Rabbit, RabbitAbandoned, RabbitImage, RabbitLitter, RabbitWeight, RabbitFeed

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

    is_kit = rabbit.date_of_birth and rabbit.date_of_birth >= date.today() - timedelta(days=8*7)
    fosters = Rabbit.objects.filter(sex='F', dead=False)
    abandon_details = None
    if rabbit.abandoned:
        try:
            abandon_details = rabbit.abandonment_details
        except RabbitAbandoned.DoesNotExist:
            abandon_details = None

    weights = RabbitWeight.objects.filter(rabbit_id=rabbit)
    last_weight = weights.order_by('-date').first()
    feeds = RabbitFeed.objects.filter(rabbit=rabbit).order_by('-date', 'feed_number')
    day = date.today()
    daily_feeds = []
    data = {}
    max_feed_number = 0
    if len(feeds) > 0:
        for feed in feeds:
            if feed.date != day:
                daily_feeds.append(data)
                data.clear()
                day = feed.date
                data["date"] = day
                data["feeds"] = []
            data["feeds"].append(feed.amount)
            data["feed_amount"] += feed.amount
            if feed.feed_number > max_feed_number:
                max_feed_number = feed.feed_number
        
    suggested_feeds = {}
    if last_weight:
        suggested_feeds["amount"] = round(float(last_weight.weight) * 0.2, 2)
        suggested_feeds["suggested_feeds"] = 2
        suggested_feeds["suggested_amount"] = round(suggested_feeds["suggested_feeds"] * suggested_feeds["amount"], 2)
        if len(feeds) > 0:
            days_feeds = feeds.filter(date__date=date.today)
            suggested_feeds = calculate_feeds(days_feeds, suggested_feeds)

    file_uploader = {
        "widget_id":    "myUpload",
        "label":        "Add Images",
        "hidden_name":  "attachments",
        "hidden_value": "[]",
    }
    return render(request, 'rabbit_detail.html', {'rabbit': rabbit, 
                                                  'buck': buck, 
                                                  'doe': doe, 
                                                  'parents': parents, 
                                                  'litters':litters, 
                                                  'images':images, 
                                                  'image_upload': file_uploader, 
                                                  'kit': is_kit, 
                                                  'fosters': fosters, 
                                                  'abandon_details': abandon_details,
                                                  'weights': weights,
                                                  'feed': suggested_feeds,
                                                  'feeds': daily_feeds,
                                                  'max_feed_number': range(max_feed_number)
                                                  })


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

def rabbit_abandon(request, pk):
    rabbit = get_object_or_404(Rabbit, pk=pk)
    is_abandoned = bool(request.POST.get('abandoned'))
    abandon_reason = request.POST.get('reason', '')
    abandon_date_str = request.POST.get('date')
    foster_mom_id = request.POST.get('foster_mom')
    foster_mom = None
    if foster_mom_id and foster_mom_id.isdigit():
        try:
            foster_mom = Rabbit.objects.get(pk=foster_mom_id)
        except Rabbit.DoesNotExist:
            foster_mom = None
    abandoned_db = RabbitAbandoned.objects.filter(rabbit=rabbit).first()
    if rabbit.abandoned:
        if is_abandoned:
            if abandoned_db:
                abandoned_db.reason = abandon_reason
                abandoned_db.date = abandon_date_str
                abandoned_db.foster_mom = foster_mom
                abandoned_db.save()
            else:
                RabbitAbandoned.objects.create(
                    rabbit=rabbit,
                    reason=abandon_reason,
                    date=abandon_date_str,
                    foster_mom=foster_mom
                )
        else:
            rabbit.abandoned = False
            rabbit.save()
            if abandoned_db:
                abandoned_db.delete()
    else:
        if is_abandoned:
            if abandoned_db:
                abandoned_db.reason = abandon_reason
                abandoned_db.date = abandon_date_str
                abandoned_db.foster_mom = foster_mom
                abandoned_db.save()
            else:
                RabbitAbandoned.objects.create(
                    rabbit=rabbit,
                    reason=abandon_reason,
                    date=abandon_date_str,
                    foster_mom=foster_mom
                )
        else:
            if abandoned_db:
                abandoned_db.delete()
    messages.success(request, 'Updated abandonment status for rabbit: {}'.format(rabbit))
    return JsonResponse({'status': 'success'})

def rabbit_weight(request, pk):
    rabbit = get_object_or_404(Rabbit, pk=pk)
    weights = [v for k, v in request.POST.items() if k.startswith('weight_value_')]
    date_strs = [v for k, v in request.POST.items() if k.startswith('weight_date_')]
    messages= []
    for weight, date_str in zip(weights, date_strs):
        date_of_weight = None
        if date_str:
            try:
                date_of_weight = date.fromisoformat(date_str)
            except Exception:
                date_of_weight = None
        if weight and date_of_weight:
            RabbitWeight.objects.create(
                rabbit=rabbit,
                weight=weight,
                date=date_of_weight
            )
            messages.append({'tags': 'success', 'message': 'Added weight for rabbit: {}'.format(rabbit)})
        else:
            messages.append({'tags': 'error', 'message': 'Invalid weight or date. Please try again.'})
    return JsonResponse({'type': 'success', 'messages': messages, 'button': 'btnWeightSave'}, safe=False)

def rabbit_feed(request, pk):
    number_of_feeds = request.POST.get("feeds")
    feed_amount = request.POST.get("feed_amount")
    suggested_total = request.POST.get("suggestedTotal") if request.POST.get("suggestedTotal") != "" else 0
    suggested_feeds = request.POST.get("suggestedFeeds") if request.POST.get("suggestedFeeds") != "" else 2
    suggested_amount = request.POST.get("suggestedAmounts") if request.POST.get("suggestedAmounts") != "" else 0
    
    rabbit = get_object_or_404(Rabbit, pk=pk)
    feeds = RabbitFeed.objects.filter(rabbit=rabbit).filter(date__date=date.today)
    feed_number = 1
    if len(feeds) != 0:
        feed_number = feeds.order_by("-feed_number").first().feed_number + 1
    messages = []
    feed_suggestion = {"total_amount": 0, "feeds":0, "amount":0}

    if feed_amount != "":
        RabbitFeed.objects.create(
            rabbit = rabbit,
            amount = feed_amount,
            feed_number = feed_number,
            date = date.now
        )

    if number_of_feeds != "":
        if len(feeds) + 1 >= number_of_feeds:
            messages.append({'tags': 'error', 'message': 'Invalid number of feeds. Please set a valid number'})
        else:
            feed_suggestion["feeds"] = number_of_feeds
    
    feed_suggestion = calculate_feeds(feeds, feed_suggestion)

    return JsonResponse()

def calculate_feeds(feeds, feed_suggestion):
    total_amount = feed_suggestion["total_amount"]
    no_of_feeds = feed_suggestion["feeds"]
    feed_amount = feed_suggestion["amount"]
    feeds_left = no_of_feeds - len(feeds)
    amount_left = total_amount
    for feed in feeds:
        amount_left -= feed.amount
    if feeds_left == 0:
        feeds_left = 1
        feed_suggestion["feeds"] += 1
    
    feed_amount = amount_left/feeds_left
    feed_suggestion["amount"] = feed_amount
    return feed_suggestion
