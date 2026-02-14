from django.contrib import admin
from .models import Rabbit


@admin.register(Rabbit)
class RabbitAdmin(admin.ModelAdmin):
	list_display = ('id', 'name', 'breed', 'sex', 'date_of_birth')
	search_fields = ('name', 'breed')
