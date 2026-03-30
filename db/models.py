from re import split

from django.db import models

class Rabbit(models.Model):
	SEX_CHOICES = [
		('M', 'Buck'),
		('F', 'Doe'),
		('U', 'Unsexed'),
	]

	name = models.CharField(max_length=100, null=True, blank=True)
	image = models.ImageField(upload_to='rabbits/', null=False, blank=False, default="rabbits/Default.png") # change to refence to image
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
	abandoned = models.BooleanField(default=False)

	def __str__(self):
		return self.name or f'Rabbit {self.pk}'
	

class RabbitImage(models.Model):
	image_id = models.AutoField(primary_key=True)
	rabbit_id = models.ForeignKey(Rabbit, on_delete=models.CASCADE, related_name='rabbit')
	image = models.ImageField(upload_to='rabbits/', null=False, blank=False)

class RabbitLitter(models.Model):
	litter_id = models.AutoField(primary_key=True)
	litter_number = models.IntegerField(null=False, blank=False)
	buck = models.ForeignKey(Rabbit, on_delete=models.CASCADE, null=True, blank=True, related_name='litter_buck')
	doe = models.ForeignKey(Rabbit, on_delete=models.CASCADE, null=True, blank=True, related_name='litter_doe')
	rabbit = models.ForeignKey(Rabbit, on_delete=models.CASCADE)
	litter_date = models.DateField(null=True, blank=True)
	abandoned = models.BooleanField(default=False)

	def __int__(self):
		return self.litter_id or f'Litter {self.pk}'
	
class RabbitAbandoned(models.Model):
	abandon_id = models.AutoField(primary_key=True)
	rabbit = models.OneToOneField(Rabbit, on_delete=models.CASCADE, related_name='abandonment_details')
	reason = models.TextField(blank=True)
	date = models.DateField(null=True, blank=True)
	foster_mom = models.ForeignKey(Rabbit, on_delete=models.SET_NULL, null=True, blank=True, related_name='fostered_kits')

	def __int__(self):
		return self.abandon_id or f'Abandonment {self.pk}'

class RabbitWeight(models.Model):
	weight_id = models.AutoField(primary_key=True)
	rabbit = models.ForeignKey(Rabbit, on_delete=models.CASCADE, related_name='weights')
	weight = models.DecimalField(max_digits=5, decimal_places=2)
	date = models.DateField()

	def __int__(self):
		return self.weight_id or f'Weight {self.pk}'
