from django.contrib import admin
from django.urls import path
from . import views

app_name='fontsapp'

urlpatterns=[
    path('input_phrase/', views.input_phrase, name='input_phrase'),
    path('no_checkpoint/<int:input_id>', views.no_checkpoint, name='no_checkpoint'),
    path('input_choice/<int:input_id>', views.input_choice, name='input_choice'),
    path('scan_input/<int:input_id>', views.scan_input, name='scan_input'),
    path('write_input/<int:input_id>', views.write_input, name='write_input'),
    path('input_edit/<int:input_id>', views.input_edit, name='input_edit'),
    path('loading/<int:input_id>', views.loading, name='loading'),
    path('result/<int:input_id>', views.result, name='result'),
]