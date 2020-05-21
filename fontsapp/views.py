from django.shortcuts import render

# Create your views here.

def home(request) :
    return render(request, 'home.html')

def input(request):
    return render(request, 'input.html')

def input_edit(request):
    return render(request, 'input_edit.html')

def loading(request):
    return render(request, 'loading.html')

def result(request):
    return render(request, 'result.html')