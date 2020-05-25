from django import forms
from .models import Font

class FontForm(forms.ModelForm):
    class Meta:
        model = Font
        fields=['phrase', 'input_photo1', 'output_photo1']
