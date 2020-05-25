from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import auth

# Create your views here.

def signup(request) :
    if request.method=='POST' : ## 유저 로그인 버튼 누를때
        if request.POST['password1'] == request.POST['password2'] :
            try :  # 아이디 이미 존재
                user = User.objects.get(username=request.POST['username'])
                return render(request, 'signup.html', {'error':'이미 존재하는 아이디입니다.'})

            except User.DoesNotExist:
                # 회원가입
                user = User.objects.create_user(  
                    request.POST['username'], password=request.POST['password1'], email=request.POST['email'])
                user.first_name = request.POST['firstname']
                user.last_name = request.POST['lastname']
                user.save()
                auth.login(request, user)
                return redirect('home')
        
        else:  ## pw1과 pw2 다를 때
            return render(request, 'signup.html', {'error' : '비밀번호가 일치하지 않습니다.'})
    
    else :  ## 유저 정보 입력
        return render(request, 'signup.html')


def login(request) :
    if request.method == 'POST' :   # 로그인 버튼 눌렀을 때
        username = request.POST['username']
        password = request.POST['password']
        user = auth.authenticate(request, username=username, password=password)

        if user is not None : #사용자 정보 맞게 입력
            auth.login(request, user)
            return redirect('home')

        else : # 잘못 입력 
            return render(request, 'login.html', {'error' : 'id나 비밀번호가 틀립니다.'})
    
    else : #잘못 입력
        return render(request, 'login.html')


def logout(request) : 
    if request.method == 'POST' :
        auth.logout(request)
        return redirect('home')

    return render(request, 'signup.html')