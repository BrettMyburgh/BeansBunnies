from django.core.management.base import BaseCommand
from db.models import Rabbit, RabbitImage # type: ignore

class Command(BaseCommand):

    def handle(self, *args, **options):
        rabbits = Rabbit.objects.all()
        for rabbit in rabbits:
            existing_image = RabbitImage.objects.filter(rabbit_id = rabbit).first()
            if existing_image != None:
                if rabbit.image.name != "rabbits/Default.png":
                    if rabbit.image.url != existing_image.image.url:
                        rabbit.image.delete()
                    rabbit.image = existing_image.image
                    rabbit.save()