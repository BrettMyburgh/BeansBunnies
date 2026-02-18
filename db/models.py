from django.db import models

class Rabbit(models.Model):
	SEX_CHOICES = [
		('M', 'Buck'),
		('F', 'Doe'),
		('U', 'Unsexed'),
	]

	name = models.CharField(max_length=100)
	image = models.ImageField(upload_to='rabbits/', null=True, blank=False)
	parent = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='children')
	breed = models.CharField(max_length=100, blank=True)
	date_of_birth = models.DateField(null=True, blank=False)
	sex = models.CharField(max_length=1, choices=SEX_CHOICES, blank=False)
	created = models.DateTimeField(auto_now_add=True)
	dead = models.BooleanField(default=False)
	date_of_death = models.DateField(null=True, blank=True)
	cause_of_death = models.TextField(blank=True)

	def __str__(self):
		return self.name or f'Rabbit {self.pk}'