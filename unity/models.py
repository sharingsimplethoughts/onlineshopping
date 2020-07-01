from django.db import models
from django.contrib.auth.models import User
from product.models import Product
GENDER = (('1', 'male'),('2', 'female'),('3', 'kids'))
# Create your models here.

class UserBodyMeasurementData(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    gender= models.CharField(max_length=20, choices=GENDER)
    # measurement data
    height = models.CharField(max_length=20, default=0)
    chest = models.CharField(max_length=20, default=0)
    butts = models.CharField(max_length=20, default=0)
    waist = models.CharField(max_length=20, default=0)
    thigh = models.CharField(max_length=20, default=0)
    arm = models.CharField(max_length=20, default=0)

    # product

    product = models.ForeignKey(Product, blank=True, null=True, on_delete=models.CASCADE)



    def __int__(self):
        return self.user.id



