from django import forms
from .models import Font

class FontForm(forms.ModelForm):
    class Meta:
        model = Font
        fields=['phrase1', 'phrase2', 'template_img', 'input_photo1', 'output_photo1']
