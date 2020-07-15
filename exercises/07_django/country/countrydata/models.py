from django.db import models


class Continent(models.Model):

    name = models.CharField(max_length=255, unique=True)
    code = models.CharField(max_length=255, unique=True)

    class Meta:
        ordering = ['name']

class Country(models.Model):

    name = models.CharField(max_length=255)
    capital = models.CharField(max_length=255)
    code = models.CharField(max_length=255, unique=True)
    population = models.PositiveIntegerField(default=0)
    area = models.PositiveIntegerField(default=0)
    continent = models.ForeignKey(Continent, related_name="countries", on_delete=models.CASCADE)

    class Meta:
        ordering = ['name']
