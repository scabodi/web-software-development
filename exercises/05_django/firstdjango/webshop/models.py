from django.db import models

class Product(models.Model):
    """
    Write your model for the exercise 3 here. Remove the pass text.
    """
    title = models.CharField(max_length=255, unique=True)
    description = models.TextField(default='')
    image_url = models.URLField(blank=True)
    quantity = models.IntegerField(default=0) #should it be positive?

    def sell(self):
        self.quantity -= 1
        self.save()
