from django.core.management.base import BaseCommand
from django.db.models.aggregates import Max
from db.models import Rabbit, RabbitImage, RabbitLitter # type: ignore

class Command(BaseCommand):

    def handle(self, *args, **options):
        rabbits = Rabbit.objects.all()
        litters = RabbitLitter.objects.all()
        # get children
        fathered = rabbits.filter(buck__isnull = False)
        mothered = rabbits.filter(doe__isnull = False)
        combined_parented = list(set(list(fathered) + list(mothered)))
        # get parents
        for rabbit in combined_parented:
            filtered_litters = litters.filter(buck=rabbit.buck, doe = rabbit.doe, litter_date = rabbit.date_of_birth)
            if filtered_litters.exists():
                litter_number = filtered_litters.first().litter_number
                existing_litter = filtered_litters.filter(rabbit=rabbit)
                if existing_litter.exists() == False:
                    RabbitLitter.objects.create(
                        litter_number= litter_number,
                        buck= rabbit.buck,
                        doe= rabbit.doe,
                        rabbit = rabbit,
                        litter_date = rabbit.date_of_birth
                    )
            else:
                filtered_litters = litters.filter(buck=rabbit.buck, doe = rabbit.doe)
                if filtered_litters.exists():
                    litter_number = filtered_litters.aggregate(Max('litter_date'))['litter_date__max']
                    RabbitLitter.objects.create(
                        litter_number= litter_number,
                        buck= rabbit.buck,
                        doe= rabbit.doe,
                        rabbit = rabbit,
                        litter_date = rabbit.date_of_birth
                    )
                else:
                    RabbitLitter.objects.create(
                        litter_number= 1,
                        buck= rabbit.buck,
                        doe= rabbit.doe,
                        rabbit = rabbit,
                        litter_date = rabbit.date_of_birth
                    )
        # check for litter number
        # add litter

            