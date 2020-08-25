# -*- coding: utf-8 -*-
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .forms import FontForm
from .models import Font
import cv2
import os
from PIL import Image
import re
import base64
from matplotlib import pyplot as plt


# Create your views here.

def home(request) :
    return render(request, 'home.html')

#create
@login_required
def input_phrase(request): 
    ## 입력 문구 작성 ##
    
    chars = ['눈', '송', '이', '는', '졸', '업', '을', '꿈', '꾸', '지']  # 체크포인트 있는 글자 리스트    
    not_exists = ""  # 없는 글자 --> 데베에 추가하기

    if request.method=='POST': # 제출 버튼 눌렀을 때
        form = FontForm(request.POST) # 폼 내용 받아오기

        if form.is_valid(): # 폼 형식이 유효하면 
            p1 = form.data['phrase1']

            for i in range(len(p1)) : # p1 검사
                if p1[i] not in chars :
                    not_exists += p1[i]

            if len(not_exists) == 0 : #없는 글자 없으면
                font = form.save(commit=False)
                font.user = request.user # 현재 유저 저장
                font.final_phrase = p1
                font.save() # 저장
                return redirect('fontsapp:input_choice', input_id=font.pk) #다음단계로. pk값 같이 넘겨주기

            else : # 없는 글자 있으면
                font = form.save(commit=False)
                font.user = request.user #현재 유저 저장
                font.no_checkpoint = not_exists #없는 글자
                
                # 없는 글자 빼고 문장 완성해주기 
                final = ""
                for char1 in p1 : 
                    if char1 in not_exists:
                        pass
                    else : 
                        final += char1
                    
                font.final_phrase = final 
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

    letters = ['dummy2' ,'moon', 'ip', 'cho', 'gi', 'web', 'dummy1', 'dae', 'yeo', 'myung', 'sook' ] #현재 결과에 맞춰놓음!! 나중에 바꾸기!!

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
                        cropname = letters[index]
                        
                        day = str(font.date)[:10]
                        time = str(font.date)[11:13] + "-" + str(font.date)[14:16]
                        day_time = day + "_" + time
                        cv2.imwrite("./media/crop/"+str(request.user) + "_" + day_time + "_" + cropname+'.png', cropped)
                        
                    index+=1

            ## 자른 이미지 데이터베이스에 저장 ##
            # 이미지 순서 맞춰서 저장하기
            # 현재 숙&명 만 저장
            day = str(font.date)[:10]
            time = str(font.date)[11:13] + "-" + str(font.date)[14:16]
            day_time = day + "_" + time

            sook = "./crop/"+ str(request.user) + "_" + day_time + "_" +'sook.png' # 숙
            myung = "./crop/"+ str(request.user) + "_" + day_time + "_" +'myung.png' # 명
            yeo = "./crop/"+ str(request.user) + "_" + day_time + "_" +'yeo.png' # 여
            dae = "./crop/"+ str(request.user) + "_" + day_time + "_" +'dae.png' # 대
            
            font.input_photo1 = sook 
            font.input_photo2 = myung
            font.input_photo3 = yeo
            font.input_photo4 = dae
            font.save(update_fields=['input_photo1', 'input_photo2', 'input_photo3', 'input_photo4']) # 데베에 저장

            return redirect('fontsapp:input_edit', input_id=font.pk) # 이미지 편집단계로. pk값 유지
    
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
        day = str(font.date)[:10]
        time = str(font.date)[11:13] + "-" + str(font.date)[14:16]
        day_time = day + "_" + time

        filename1 = str(request.user) + "_" + day_time + "_" +'sook.png'
        filename2 = str(request.user) + "_" + day_time + "_" +'myung.png'

        #'wb'로 파일 open
        image1 = open(path+filename1, "wb")
        image2 = open(path+filename2, "wb")

        #디코딩 + 파일에 쓰기
        image1.write(base64.b64decode(data1))
        image2.write(base64.b64decode(data2))
        
        
        image1.close()
        image2.close()

        sook = "./crop/"+ str(request.user) + "_" + day_time + "_" +'sook.png' # 숙
        myung = "./crop/"+ str(request.user) + "_" + day_time + "_" +'myung.png' # 명
        
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

    # 이미지 복사 #
    phrase_kor = ['dummy2','dummy1','문','입','초','기','웹','대','여','명','숙']
    phrase_eng = ['dummy2','dummy1','moon','ip','cho','gi','web','dae','yeo','myung','sook'] #dummy는 index맞추기 위함! 나중에 고치기
    dictionary = {'이':'여', '지':'기', '송':'초', '졸':'초', '업':'입', '눈':'문', '는':'문', '을':'문', '꿈':'문', '꾸':'문'}

    # 파일명
    day = str(font.date)[:10]
    time = str(font.date)[11:13] + "-" + str(font.date)[14:16]
    day_time = day + "_" + time


    # 디렉토리에 파일 복사
    mkdir_command = " mkdir ./media/result/" + str(request.user) + "_" + day_time # 이미지 병합 위한 디렉토리 만들기
    os.system(mkdir_command)

    for i in range(10,1,-1) : #지금은 숙.명.여.대. 까지만! 나중에 고치기
        
        #글자별로 유저 폴더 생성
        char = phrase_kor[i] #숙.명.여.대. 돌아가면서
        mkdir_command = " mkdir ~/ganjyfont/test2/" + str(char) + "/" + str(request.user) + "_" + day_time #학습 돌릴 이미지 모아두는 디렉토리
        os.system(mkdir_command)
        
        
        picname =  str(request.user) + "_" + day_time + "_" + phrase_eng[i] + ".png" # 숙
        cp_command = "cp ~/WebServer/Graduate/media/crop/" + picname +  " ~/ganjyfont/test2/" + str(char) + "/" + str(request.user) + "_" + day_time + "/"
        os.system(cp_command) #파일 복사

    
    # 명령어 완성
    input_str = str(font.final_phrase) #checkpoint 있는 문자들 + * 로만 되어있는 문구
    
    # ex) 문->을
    filename = {'숙':'sook', '명':'myung', '여':'yeo', '대':'dae', '웹':'web', '기':'gi', '초':'cho', '입':'ip', '문':'moon' }

    for char, i in zip(input_str, range(len(input_str))) : #char=만들 글자 (을 이)
        if char=="*" :
            pass
        else : 
            #이미지 생성
            letter = dictionary[char] #letter=체크포인트 글자 (문 여)
            dl_command = "cd ~/ganjyfont && python3 test.py --dataroot ~/ganjyfont/test2/" + letter + "/" + str(request.user) + "_" + day_time + " --name " + letter + "_" + char + "_pix2pix --model test --which_model_netG unet_256 --which_direction AtoB --dataset_mode single --norm batch --gpu_ids=0 --how_many=100"
            print("=================deep learning=================")
            os.system(dl_command)

            
            #이미지 복사 --> 이미지 병합하기 위함!
            beforecopy = "~/ganjyfont/results_ver2_font/" + letter + "_" + char +"_pix2pix/test_latest/images/" + str(request.user) + "_" + day_time + "_" + filename[letter] + "_fake_B.png"
            aftercopy = "./media/result/" + str(request.user) + "_" + day_time + "/" + str(i) + ".png"
            cp_command = "cp " + beforecopy + " " + aftercopy
            os.system(cp_command)
    

    
    #이미지 이어붙이기
    print("=============image merge===============")
    string = input_str

    directory = './media/result/'+ str(request.user) + "_" + day_time 
    for i in range(len(string)) :
        if i is 0:
            result = directory + "/" +  str(i) +'.png'
            print(result)
            result = cv2.imread(result, 1)
        else:    
            temp = directory + "/" + str(i) +'.png'
            print(temp)
            temp = cv2.imread(temp, 1)
            result = cv2.hconcat([result, temp])

    # 결과 이미지 경로 지정
    # 결과 이미지 webserver/Graduate/media/output 경로에 저장하기
    imgName = "./media/output/" + str(request.user) + "_" + day_time  + "_result.png"
    cv2.imwrite(imgName, result)
    
    # 이미지 db에 저장
    output_photo = "./output/" + str(request.user) + "_" + day_time  + "_result.png"
    font.output_photo1 = output_photo
    font.save(update_fields=['output_photo1']) # 데베에 저장

    return render(request, 'loading.html', {'font':font})


#read
@login_required
def result(request, input_id):
    ## 결과페이지 ##

    font = get_object_or_404(Font, pk=input_id)
    return render(request, 'result.html', {'font':font})


