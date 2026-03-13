from django.core.management.base import BaseCommand
from db.models import Rabbit, RabbitImage # type: ignore

class Command(BaseCommand):

    def handle(self, *args, **options):
        rabbits = Rabbit.objects.all()
        for rabbit in rabbits:
            existing_image = RabbitImage.objects.filter(rabbit_id = rabbit).first()
            if existing_image == None:
                RabbitImage.objects.create(
                    rabbit_id=rabbit,
                    image=rabbit.image
                )