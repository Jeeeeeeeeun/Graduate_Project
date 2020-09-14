from django import forms
from .models import Font

class FontForm(forms.ModelForm):
    class Meta:
        model = Font
        fields=['phrase1', 'template_img', 'input_photo1', 'output_photo1']
        widgets = {
            'phrase1' : forms.TextInput(
                attrs={
                    'style' : 'width:800px; border:solid gray; border-radius:5px; padding:20px; text-align:center;font-family:"나눔고딕";font-size:19px;',
                    'value' : '눈송이는 졸업을 꿈꾸지',
                }
            )
        }
