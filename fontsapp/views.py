from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .forms import FontForm
from .models import Font
import cv2
import os
from PIL import Image
import re
import base64

# Create your views here.

def home(request) :
    return render(request, 'home.html')

#create
@login_required
def input_phrase(request): 
    ## 입력 문구 작성 ##
    
    chars = ['가', '나', '다', '라']  # 체크포인트 있는 글자 리스트    
    not_exists = ""  # 없는 글자 --> 데베에 추가하기

    if request.method=='POST': # 제출 버튼 눌렀을 때
        form = FontForm(request.POST) # 폼 내용 받아오기

        if form.is_valid(): # 폼 형식이 유효하면 
            p1 = form.data['phrase1']
            p2 = form.data['phrase2']

            for i in range(len(p1)) : # p1 검사
                if p1[i] not in chars :
                    not_exists += p1[i]
            
            for i in range(len(p2)): # p2 검사
                if p2[i] not in chars :
                    not_exists += p2[i]

            
            if len(not_exists) == 0 : #없는 글자 없으면
                font = form.save(commit=False)
                font.user = request.user # 현재 유저 저장
                font.save() # 저장
                return redirect('fontsapp:input_choice', input_id=font.pk) #다음단계로. pk값 같이 넘겨주기

            else : # 없는 글자 있으면
                font = form.save(commit=False)
                font.user = request.user #현재 유저 저장
                font.no_checkpoint = not_exists #없는 글자
                font.save() #저장
                return redirect('fontsapp:no_checkpoint', input_id=font.pk) #다음단계로. pk값 같이 넘겨주기

    else: # 그냥 페이지 띄울 때
        form = FontForm() # 폼 띄워주기
        return render(request, 'input_phrase.html', {'form':form})

def no_checkpoint(request, input_id) :
    font = get_object_or_404(Font, pk=input_id) # pk값 유지해서 넘겨주기 위함
    return render(request, 'no_checkpoint.html', {'font':font})


#read
@login_required
def input_choice(request, input_id):
    ## 입력 방식 정하기 ## 
    font = get_object_or_404(Font, pk=input_id) # pk값 유지해서 넘겨주기 위함
    return render(request, 'input_choice.html', {'font':font})

#update
@login_required
def scan_input(request, input_id): 
    ## 스캔 입력 ##

    # 잘라서 input-photo1, input_photo2에 넣는 로직
    # 이미지 크기 조정 필요하면 하기

    font = get_object_or_404(Font, pk=input_id) # 현재 객체 가져오기

    if request.method=='POST': # 제출 버튼 눌렀을 떄
        form = FontForm(request.POST, request.FILES, instance=font) # 폼 내용 받아오기  #이미지업로드->reqeust.FILES 넣어주기     
        if form.is_valid(): # 폼 형식이 유효하면
            font = form.save(commit=False)
            font.save(update_fields=['template_img']) # 현재 객체의 template_img란만 update

            ## 사진 글자 하나씩 자르기 ##
            img = "." + font.template_img.url   # 현재 사진
            
            img_color = cv2.imread(img, cv2.IMREAD_COLOR)
            cv2.imshow('result', img_color)
            #cv2.waitKey(0)

            img_gray = cv2.cvtColor(img_color, cv2.COLOR_BGR2GRAY)
            cv2.imshow('result', img_gray)
            #cv2.waitKey(0)

            ret, img_binary = cv2.threshold(img_gray, 127, 255, cv2.THRESH_BINARY_INV|cv2.THRESH_OTSU)
            cv2.imshow('result', img_binary)
            #cv2.waitKey(0)

            contours, hierachy = cv2.findContours(img_binary, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

            index = 0
            for cnt in contours:
                size = len(cnt)
                #print(size)

                epsilon = 0.00002 * cv2.arcLength(cnt, True)
                approx = cv2.approxPolyDP(cnt, epsilon, True) # 직선 근사화

                size = len(approx)
                #print(size)

                # if it is a rectangle
                if size is 4:
                    if index is not 6:
                        #save image
                        x,y,w,h = cv2.boundingRect(cnt)
                        cropped = img_color[y:y+h, x:x+w]
                        cropname = "crop"+str(index)
                        cv2.imwrite("./media/crop/"+ str(request.user) + "_" + cropname+'.png', cropped)
                        
                    index+=1

            ## 자른 이미지 데이터베이스에 저장 ##
            # 이미지 순서 맞춰서 저장하기
            # 현재 숙&명 만 저장
            sook = "./crop/"+ str(request.user) + "_" +'crop10.png' # 숙
            myung = "./crop/"+ str(request.user) + "_" +'crop9.png' # 명
            
            font.input_photo1 = sook 
            font.input_photo2 = myung
            font.save(update_fields=['input_photo1', 'input_photo2']) # 데베에 저장
    
    else : # 그냥 페이지 띄울 때
        form = FontForm(instance=font) # 폼에 기존 내용 넣어서 띄워주기
        return render(request, 'scan_input.html', {'form':form})


#update
@login_required
def write_input(request, input_id):
    ## 직접 입력 ##

    # canvas의 이미지 가져와서 Font.input_photo1에 저장하기
    
    if request.method=='POST': # 제출 버튼 눌렀을 떄
        font = get_object_or_404(Font, pk=input_id) #현재 객체


        data1 = request.POST.__getitem__('canvas1')
        data2 = request.POST.__getitem__('canvas2')

        
        data1=data1[22:]
        data2=data2[22:]

        #저장할 경로
        path = './media/crop/'
        filename1 = str(request.user) + "_" +'crop10.png'
        filename2 = str(request.user) + "_" +'crop9.png'

        #'wb'로 파일 open
        image1 = open(path+filename1, "wb")
        image2 = open(path+filename2, "wb")

        #디코딩 + 파일에 쓰기
        image1.write(base64.b64decode(data1))
        image2.write(base64.b64decode(data2))
        
        
        image1.close()
        image2.close()

        sook = "./crop/"+ str(request.user) + "_" +'crop10.png' # 숙
        myung = "./crop/"+ str(request.user) + "_" +'crop9.png' # 명
        
        font.input_photo1 = sook 
        font.input_photo2 = myung
        font.save(update_fields=['input_photo1', 'input_photo2']) # 데베에 저장


        return redirect('fontsapp:input_edit', input_id=font.pk) # 이미지 편집단계로. pk값 유지

    else :
        font = get_object_or_404(Font, pk=input_id)
        return render(request, 'write_input.html', {'font':font})

#update
@login_required
def input_edit(request, input_id):
    ## 사진 편집 ##

    #크기. 중앙에 맞추기 등 설정 & 변경사항 저장하기
    font = get_object_or_404(Font, pk=input_id)
    

    return render(request, 'input_edit.html', {'font':font})


@login_required
def loading(request, input_id):
    ## 로딩 페이지 ##

    # 결과 이미지 받아서 model.output_photo에 저장
    # AJAX사용하기 https://djangosnippets.org/snippets/679/

    # 현재 객체
    font = get_object_or_404(Font, pk=input_id)


    ## 딥러닝 서버 돌리기 ##
    # 결과 이미지 webserver/Graduate/media/output 경로에 저장하기


    # 결과 이미지 경로 지정
    img_name = "test_image"
    output_img = "./output/"+ img_name +".png" #이미지 이름 식별 가능하게 바꾸기!

    # 이미지 db에 저장
    font.output_photo1 = output_img
    font.save(update_fields=['output_photo1']) # 데베에 저장

    return render(request, 'loading.html', {'font':font})

#read
@login_required
def result(request, input_id):
    ## 결과페이지 ##

    font = get_object_or_404(Font, pk=input_id)
    return render(request, 'result.html', {'font':font})
