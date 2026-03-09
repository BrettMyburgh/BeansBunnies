from re import split

from django.db import models

class Rabbit(models.Model):
	SEX_CHOICES = [
		('M', 'Buck'),
		('F', 'Doe'),
		('U', 'Unsexed'),
	]

	name = models.CharField(max_length=100, null=True, blank=True)
	image = models.ImageField(upload_to='rabbits/', null=True, blank=False)
	buck = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='fathered')
	doe = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='litters')
	note = models.TextField(blank=True, null=True)
	temprament = models.CharField(max_length=200, blank=True)
	breed = models.CharField(max_length=100, blank=True)
	date_of_birth = models.DateField(null=True, blank=True)
	sex = models.CharField(max_length=1, choices=SEX_CHOICES, blank=False)
	created = models.DateTimeField(auto_now_add=True)
	dead = models.BooleanField(default=False)
	date_of_death = models.DateField(null=True, blank=True)
	cause_of_death = models.TextField(blank=True)

	def __str__(self):
		return self.name or f'Rabbit {self.pk}'
	
# class Litters(models.Model):
# 	litter_id = models.AutoField(primary_key=True)
# 	litter_number = models.IntegerField(null=False, blank=False)
# 	buck = models.ForeignKey(Rabbit, on_delete=models.CASCADE, related_name='litter_buck')
# 	doe = models.ForeignKey(Rabbit, on_delete=models.CASCADE, related_name='litter_doe')
# 	rabbit = models.ForeignKey(Rabbit, on_delete=models.CASCADE)
# 	litter_date = models.DateField(null=True, blank=True)

# 	def __int__(self):
# 		return self.litter_id or f'Litter {self.pk}'