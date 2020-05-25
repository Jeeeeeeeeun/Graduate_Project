from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .forms import FontForm
from .models import Font

# Create your views here.

def home(request) :
    return render(request, 'home.html')

#create
@login_required
def input_phrase(request):
    if request.method=='POST':
        form = FontForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            post.save()
            return redirect('fontsapp:input_choice', input_id=post.pk)
    else:
        form = FontForm()
        return render(request, 'input_phrase.html', {'form':form})

#update
@login_required
def input_choice(request, input_id):
    post = get_object_or_404(Font, pk=input_id)
    return render(request, 'input_choice.html', {'post':post})

#update
@login_required
def scan_input(request, input_id):
    post = get_object_or_404(Font, pk=input_id)
    if request.method=='POST':
        form = FontForm(request.POST, instance=post)
        if form.is_valid():
            post = form.save(commit=False)
            post.save(update_fields=['input_photo1'])
            return redirect('fontsapp:input_edit', input_id=post.pk)
    else :
        form = FontForm(instance=post)
        return render(request, 'scan_input.html', {'form':form})


#update
@login_required
def write_input(request, input_id):
    
    # canvas의 이미지 가져와서 Font.input_photo1에 저장하기
    return render(request, 'write_input.html')

#update
@login_required
def input_edit(request, input_id):
    post = get_object_or_404(Font, pk=input_id)

    return render(request, 'input_edit.html', {'post':post})


@login_required
def loading(request, input_id):
    post = get_object_or_404(Font, pk=input_id)
    return render(request, 'loading.html', {'post':post})

#read
@login_required
def result(request, input_id):
    post = get_object_or_404(Font, pk=input_id)
    return render(request, 'result.html', {'post':post})