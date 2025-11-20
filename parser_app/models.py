from django.db import models
from django.contrib.postgres.fields import ArrayField

class Phone(models.Model):

    #1. Main fields
    name = models.CharField(max_length=255, null=True)
    color = models.CharField(max_length=25, null=True)
    memory_capacity = models.CharField(max_length=10, null=True)
    price = models.CharField(max_length=100, null=True)
    price_promotion = models.CharField(max_length=100, blank=True, null=True)
    screen_diagonal = models.CharField(max_length=4, null=True)
    display_resolution = models.CharField(max_length=20, null=True)
    series = models.CharField(max_length=50, null=True)
    seller = models.CharField(max_length=255, null=True)
    product_code = models.CharField(max_length=50, null=True)
    reviews_amount = models.IntegerField(null=True)

    #2. Additional fields
    characteristics = models.JSONField(default=[], null=True)
    photos = ArrayField(models.CharField(max_length=255, null=True), null=True)

    def __str__(self):
        return self.name







