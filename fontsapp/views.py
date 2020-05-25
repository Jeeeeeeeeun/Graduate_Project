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
    ## 입력 문구 작성 view ##

    if request.method=='POST': # 제출 버튼 눌렀을 때
        form = FontForm(request.POST) # 폼 내용 받아오기
        if form.is_valid(): # 폼 형식이 유효하면 
            post = form.save(commit=False)
            post.user = request.user # 현재 유저 저장
            post.save() # 저장
            return redirect('fontsapp:input_choice', input_id=post.pk) #다음단계로. pk값 같이 넘겨주기
    
    else: # 그냥 페이지 띄울 때
        form = FontForm() # 폼 띄우주기
        return render(request, 'input_phrase.html', {'form':form})

#read
@login_required
def input_choice(request, input_id):
    ## 입력 방식 정하기 ## 
    post = get_object_or_404(Font, pk=input_id) # pk값 유지해서 넘겨주기 위함
    return render(request, 'input_choice.html', {'post':post})

#update
@login_required
def scan_input(request, input_id): 
    ## 스캔 입력 view ##

    # 템플릿 다운로드 구현해야함

    post = get_object_or_404(Font, pk=input_id) # 현재 객체 가져오기

    if request.method=='POST': # 제출 버튼 눌렀을 떄
        form = FontForm(request.POST, request.FILES, instance=post) # 폼 내용 받아오기  #이미지업로드->reqeust.FILES 넣어주기     
        if form.is_valid(): # 폼 형식이 유효하면
            post = form.save(commit=False)
            post.save(update_fields=['input_photo1']) # 현재 객체의 input_photo1란만 update
            return redirect('fontsapp:input_edit', input_id=post.pk) # 이미지 편집단계로. pk값 유지
    
    else : # 그냥 페이지 띄울 때
        form = FontForm(instance=post) # 폼에 기존 내용 넣어서 띄워주기
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