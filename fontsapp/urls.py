from django.contrib import admin
from django.urls import path
from . import views

app_name='fontsapp'

urlpatterns=[
    path('input/', views.input, name='input'),
    path('input_edit/', views.input_edit, name='input_edit'),
    path('loading/', views.loading, name='loading'),
    path('result/', views.result, name='result'),
]