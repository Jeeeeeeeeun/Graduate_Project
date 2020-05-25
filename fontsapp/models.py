from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class Font(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)
    phrase = models.CharField(blank=True, null=True, max_length=15)
    input_photo1 = models.ImageField(null=True, blank=True, upload_to='input/')
    output_photo1 = models.ImageField(null=True, blank=True, upload_to='output/')

    def __str__(self):
        a = str(self.user) + str(self.date)
        return a
