from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class Font(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE) #유저 아이디
    date = models.DateTimeField(auto_now_add=True) # 날짜
    phrase1 = models.CharField(blank=True, null=True, max_length=15) # 문구1
    phrase2 = models.CharField(blank=True, null=True, max_length=15) # 문구2
    no_checkpoint = models.CharField(blank=True, null=True, max_length=30) # 체크포인트 없는 글자
    template_img = models.ImageField(null=True, blank=True, upload_to='template_img/') # 템플릿 이미지 (손글씨 스캔해서 올림) 
    input_photo1 = models.ImageField(null=True, blank=True) # 템플릿 자른것 (글자 하나)
    input_photo2 = models.ImageField(null=True, blank=True) # 템플릿 자른것 (글자 하나)
    output_photo1 = models.ImageField(null=True, blank=True, upload_to='output/') # 생성된 이미지


    def __str__(self):
        a = str(self.user) + "_" + str(self.date)
        return a
