from django.contrib import admin
from .models import Rabbit


@admin.register(Rabbit)
class RabbitAdmin(admin.ModelAdmin):
	list_display = ('id', 'name', 'breed', 'sex', 'date_of_birth', 'dead', 'date_of_death')
	list_filter = ('dead', 'sex', 'breed')
	search_fields = ('name', 'breed')
