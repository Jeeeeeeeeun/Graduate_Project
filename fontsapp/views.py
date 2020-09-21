# -*- coding: utf-8 -*-
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponse
from .forms import FontForm
from .models import Font
import cv2
import os
from PIL import Image
import re
import base64
from matplotlib import pyplot as plt
import json
from collections import OrderedDict
import numpy as np
import threading
from django.core.mail import EmailMessage

# Create your views here.
chars = ['눈', '송', '이', '는', '졸', '업', '을', '꿈', '꾸', '지', ' ']  # 체크포인트 있는 글자 리스트    
dictionary = {'이':'여', '지':'기', '송':'숙', '졸':'초', '업':'입', '눈':'숙', '는':'문', '을':'문', '꿈':'문', '꾸':'문', ' ':'blank'}



def home(request) :
    return render(request, 'home.html')

#create
@login_required
def input_phrase(request): 
    ## 입력 문구 작성 ##
    
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


def makeFont(letter):
    pass
    # code=''

    # # open lettercode txt file
    # f = open("/home/mint/ganjyfont/lettercode.txt", 'r')
    # lines = f.readlines()

    # # find letter in lettercode and save code
    # for line in lines:
    #     if letter in line:
    #         #print(line)
    #         #print(len(line))
    #         #print(line[1:7])
    #         code = line[1:7]
    #         break

    # f.close()
    # #print(code)

    # # make json file    { "kr" : ["\uc219"] }
    # filename='/home/mint/ganjyfont/letter.json' # json dir
    
    # code = code.replace("\\/", "/").encode().decode('unicode_escape') # make unicode letter raw
    # data = { 'kr': [code] } # make json data

    # # write json data and save file
    # with open(filename, 'w', encoding='UTF-8') as file:
    #     json.dump(data, file, ensure_ascii=True, indent='\t')


# 나중에 생성하기
def create_later(request, input_id) : 
    font = get_object_or_404(Font, pk=input_id) # 사용자 생성 폰트
    font.createlater = True
    font.save()

    user = User.objects.get(username=request.user) # 사용자 정보
    userEmail = user.email

    create_list = {'순':'숙', '숨':'숙', '망':'명', '멍':'명', }

    no_chars = font.no_checkpoint
    command = "cd ~/ganjyfont; "

    for char in no_chars :
        makeFont(char)
        command += "python3 fontimg.py; "

        try : 
            command += "sh train.sh " + create_list[char] + " " + char + " 5; "
            chars.append(char)
            dictionary[char] = create_list[char]
            print(chars)
            print(dictionary)
        
        except (KeyError):
            command += "sh train.sh 문 " + char +  " 5; "
            chars.append(char)
            dictionary[char] = '문'
            print(chars)
            print(dictionary)

    t = threading.Thread(target=doTrain, args=[command, userEmail], daemon=True)
    t.start()

    font.delete()
    return redirect('home')


# 학습용 thread 함수
def doTrain(command, userEmail) :
    os.system(command)
    print("Train Finish")

    #메일 발송
    email = EmailMessage(
        "폰트 학습이 완료 되었습니다",
        "지금 바로 생성을 시작해보세요! \n http://203.153.146.28:3000",
        to = [userEmail],
    )
    email.send()


#read
@login_required
def input_choice(request, input_id):
    ## 입력 방식 정하기 ## 
    font = get_object_or_404(Font, pk=input_id) # pk값 유지해서 넘겨주기 위함
    return render(request, 'input_choice.html', {'font':font})


# https://homepages.inf.ed.ac.uk/rbf/HIPR2/unsharp.htm
def unsharp_mask(image, kernel_size=(5, 5), sigma=1.0, amount=1.0, threshold=0):
    """Return a sharpened version of the image, using an unsharp mask."""
    blurred = cv2.GaussianBlur(image, kernel_size, sigma)
    sharpened = float(amount + 1) * image - float(amount) * blurred
    sharpened = np.maximum(sharpened, np.zeros(sharpened.shape))
    sharpened = np.minimum(sharpened, 255 * np.ones(sharpened.shape))
    sharpened = sharpened.round().astype(np.uint8)
    if threshold > 0:
        low_contrast_mask = np.absolute(image - blurred) < threshold
        np.copyto(sharpened, image, where=low_contrast_mask)
    return sharpened


def canvas_image(canvasId, filename, request) :
    data = request.POST.__getitem__(canvasId)[22:]

    filename = filename + ".png"
    image = open('./media/crop/'+filename, 'wb')
    image.write(base64.b64decode(data))
    image.close()


#update
@login_required
def scan_input(request, input_id): 
    ## 스캔 입력 ##

    # 잘라서 input-photo1, input_photo2에 넣는 로직
    # 이미지 크기 조정 필요하면 하기

    letters = ['moon', 'ip', 'cho', 'gi', 'web', 'dae', 'yeo', 'myung', 'sook' ] #현재 결과에 맞춰놓음!! 나중에 바꾸기!!

    font = get_object_or_404(Font, pk=input_id) # 현재 객체 가져오기

    if request.method=='POST': # 제출 버튼 눌렀을 떄
        form = FontForm(request.POST, request.FILES, instance=font) # 폼 내용 받아오기  #이미지업로드->reqeust.FILES 넣어주기     
        if form.is_valid(): # 폼 형식이 유효하면
            font = form.save(commit=False)
            font.save(update_fields=['template_img']) # 현재 객체의 template_img란만 update


            ## 사진 글자 하나씩 자르기 ##
            template = "." + font.template_img.url
            img = cv2.imread(template)

            imgray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
            ret,thresh = cv2.threshold(imgray,127,255,0)
            contours, hierarchy = cv2.findContours(thresh,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)

            # 가장 밖의 사각형 안쪽만 저장
            cnt = contours[2]
            X,Y,W,H = cv2.boundingRect(cnt)
            detected = img[Y:Y+H, X:X+W]

            imgray = cv2.cvtColor(detected,cv2.COLOR_BGR2GRAY)
            ret,thresh = cv2.threshold(imgray,127,255,0)
            contours, hierarchy = cv2.findContours(thresh,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)

            char_list = ['문','입','초','기','웹','대','여','명','숙']
            index = 0

            # 크기로 검출
            for i in range(0,len(contours),2):
                x,y,w,h = cv2.boundingRect(contours[i])
                w_percent = w/W*100
                h_percent = h/H*100

                if 10<w_percent and w_percent<15 and 20<h_percent and h_percent<25:
                    cropped = detected[y+5:y+h-5, x+5:x+w-5]
                    cropped = cv2.resize(cropped, (256,256), interpolation=cv2.INTER_CUBIC)
                    cropped = unsharp_mask(cropped)
                    cropname = str(letters[index])
                    # 경로 및 이름 설정

                    day = str(font.date)[:10]
                    time = str(font.date)[11:13] + "-" + str(font.date)[14:16]
                    day_time = day + "_" + time
                    cv2.imwrite("./media/crop/"+str(request.user) + "_" + day_time + "_" + cropname+'.png', cropped)
                    index+=1 

            print('done!')


            ## 자른 이미지 데이터베이스에 저장 ##
            # 이미지 순서 맞춰서 저장하기
            # 현재 숙&명 만 저장
            day = str(font.date)[:10]
            time = str(font.date)[11:13] + "-" + str(font.date)[14:16]
            day_time = day + "_" + time
            userTime = str(request.user) + "_" + day_time + "_"   


            sook = "./crop/"+ userTime +'sook.png' # 숙
            myung = "./crop/"+ userTime +'myung.png' # 명
            yeo = "./crop/"+ userTime +'yeo.png' # 여
            dae = "./crop/"+ userTime +'dae.png' # 대
            web = "./crop/"+ userTime +'web.png' # 웹
            gi = "./crop/"+ userTime +'gi.png' # 기
            cho = "./crop/"+ userTime +'cho.png' # 초
            ip = "./crop/"+ userTime +'ip.png' # 입
            moon = "./crop/"+ userTime +'moon.png' # 문
            
            font.input_photo1 = sook 
            font.input_photo2 = myung
            font.input_photo3 = yeo
            font.input_photo4 = dae
            font.input_photo5 = web
            font.input_photo6 = gi
            font.input_photo7 = cho
            font.input_photo8 = ip
            font.input_photo9 = moon

            font.save(update_fields=['input_photo1', 'input_photo2', 'input_photo3', 'input_photo4', 'input_photo5', 'input_photo6', 'input_photo7', 'input_photo8', 'input_photo9']) # 데베에 저장

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

        #저장할 경로
        day = str(font.date)[:10]
        time = str(font.date)[11:13] + "-" + str(font.date)[14:16]
        day_time = day + "_" + time
        userTime = str(request.user) + "_" + day_time + "_"   

        # canvas 이미지 저장
        canvas_image('canvas', userTime + 'sook', request)
        canvas_image('canvas2', userTime + 'myung', request)
        canvas_image('canvas3', userTime + 'yeo', request)
        canvas_image('canvas4', userTime + 'dae', request)
        canvas_image('canvas5', userTime + 'web', request)
        canvas_image('canvas6', userTime + 'gi', request)
        canvas_image('canvas7', userTime + 'cho', request)
        canvas_image('canvas8', userTime + 'ip', request)
        canvas_image('canvas9', userTime + 'moon', request)


        #DB에 저장
        sook = "./crop/"+ userTime +'sook.png' # 숙
        myung = "./crop/"+ userTime +'myung.png' # 명
        yeo = "./crop/"+ userTime +'yeo.png' # 명
        dae = "./crop/"+ userTime +'dae.png'
        web = "./crop/"+ userTime +'web.png'
        gi = "./crop/"+ userTime +'gi.png'
        cho = "./crop/"+ userTime +'cho.png'
        ip = "./crop/"+ userTime +'ip.png'
        moon= "./crop/"+ userTime +'moon.png'


        font.input_photo1 = sook 
        font.input_photo2 = myung
        font.input_photo3 = yeo
        font.input_photo4 = dae
        font.input_photo5 = web
        font.input_photo6 = gi
        font.input_photo7 = cho
        font.input_photo8 = ip
        font.input_photo9 = moon

        
        font.save(update_fields=['input_photo1', 'input_photo2', 'input_photo3', 'input_photo4', 'input_photo5', 'input_photo6', 'input_photo7', 'input_photo8', 'input_photo9']) # 데베에 저장


        return HttpResponse() # 이미지 편집단계로. pk값 유지

    else :
        font = get_object_or_404(Font, pk=input_id)
        return render(request, 'write_input.html', {'font':font})

#update
@login_required
def input_edit(request, input_id):
    if request.method=='POST':
        font = get_object_or_404(Font, pk=input_id) #현재 객체

        #저장할 경로
        day = str(font.date)[:10]
        time = str(font.date)[11:13] + "-" + str(font.date)[14:16]
        day_time = day + "_" + time
        userTime = str(request.user) + "_" + day_time + "_"   

        # canvas 이미지 저장
        canvas_image('canvas', userTime + 'sook', request)
        canvas_image('canvas22', userTime + 'myung', request)
        canvas_image('canvas33', userTime + 'yeo', request)
        canvas_image('canvas44', userTime + 'dae', request)
        canvas_image('canvas55', userTime + 'web', request)
        canvas_image('canvas66', userTime + 'gi', request)
        canvas_image('canvas77', userTime + 'cho', request)
        canvas_image('canvas88', userTime + 'ip', request)
        canvas_image('canvas99', userTime + 'moon', request)

        #DB에 저장
        sook = "./crop/"+ userTime +'sook.png' # 숙
        myung = "./crop/"+ userTime +'myung.png' # 명
        yeo = "./crop/"+ userTime +'yeo.png' # 명
        dae = "./crop/"+ userTime +'dae.png'
        web = "./crop/"+ userTime +'web.png'
        gi = "./crop/"+ userTime +'gi.png'
        cho = "./crop/"+ userTime +'cho.png'
        ip = "./crop/"+ userTime +'ip.png'
        moon= "./crop/"+ userTime +'moon.png'

        font.input_photo1 = sook 
        font.input_photo2 = myung
        font.input_photo3 = yeo
        font.input_photo4 = dae
        font.input_photo5 = web
        font.input_photo6 = gi
        font.input_photo7 = cho
        font.input_photo8 = ip
        font.input_photo9 = moon

        
        font.save(update_fields=['input_photo1', 'input_photo2', 'input_photo3', 'input_photo4', 'input_photo5', 'input_photo6', 'input_photo7', 'input_photo8', 'input_photo9']) # 데베에 저장


        return HttpResponse() # 이미지 편집단계로. pk값 유지

    else:
        ## 사진 편집 ##
        #크기. 중앙에 맞추기 등 설정 & 변경사항 저장하기
        font = get_object_or_404(Font, pk=input_id)
        return render(request, 'input_edit.html', {'font':font})


def morph(img):
    # 노이즈 제거
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (8,8))
    closing = cv2.morphologyEx(img, cv2.MORPH_CLOSE, kernel)
    return closing

def cleanside(img):
    # 양 옆 25픽셀 정도만 클린
    img[:256, :26] = 255
    img[:256, 230:256] = 255
    # 위 10픽셀
    img[:10,0:256] = 255
    return img

@login_required
def loading(request, input_id):
    if request.method=='POST': # 시작 버튼 눌렀을 떄
        font = get_object_or_404(Font, pk=input_id) # 현재 객체
        ## 딥러닝 서버 돌리기 ##

        ##### 1. 이미지 복사 #####
        phrase_kor = ['문','입','초','기','웹','대','여','명','숙']
        phrase_eng = ['moon','ip','cho','gi','web','dae','yeo','myung','sook'] #dummy는 index맞추기 위함! 나중에 고치기

        # 파일명
        day = str(font.date)[:10]
        time = str(font.date)[11:13] + "-" + str(font.date)[14:16]
        day_time = day + "_" + time
        userTime = str(request.user) + "_" + day_time + "_"   


        # 디렉토리에 파일 복사
        mkdir_command = " mkdir ./media/result/" + str(request.user) + "_" + day_time # 이미지 병합 위한 디렉토리 만들기
        os.system(mkdir_command)

        for i in range(8,-1,-1) : 
            #글자별로 유저 폴더 생성
            char = phrase_kor[i] #숙.명.여.대. 돌아가면서
            mkdir_command = " mkdir ~/ganjyfont/test2/" + str(char) + "/" + str(request.user) + "_" + day_time #학습 돌릴 이미지 모아두는 디렉토리
            os.system(mkdir_command)       
            
            picname =  userTime + phrase_eng[i] + ".png" # 숙
            cp_command = "cp ~/WebServer/Graduate/media/crop/" + picname +  " ~/ganjyfont/test2/" + str(char) + "/" + str(request.user) + "_" + day_time + "/"
            os.system(cp_command) #파일 복사x`
        

        ##### 2.딥러닝 돌리기 #####
        
        # 명령어 완성
        input_str = str(font.final_phrase) #checkpoint 있는 문자들 + * 로만 되어있는 문구
        
        filename = {'숙':'sook', '명':'myung', '여':'yeo', '대':'dae', '웹':'web', '기':'gi', '초':'cho', '입':'ip', '문':'moon' }

        for char, i in zip(input_str, range(len(input_str))) : #char=만들 글자 (을)
            if char==" " :
                pass
            else : 
                #이미지 생성
                letter = dictionary[char] #letter=체크포인트 글자 (문)
                dl_command = "cd ~/ganjyfont && python3 test.py --dataroot ~/ganjyfont/test2/" + letter + "/" + str(request.user) + "_" + day_time + " --name " + letter + "_" + char + "_pix2pix --model test --which_model_netG unet_256 --which_direction AtoB --dataset_mode single --norm batch --gpu_ids=0 --how_many=100"
                print("=================deep learning=================")
                os.system(dl_command)
                
                #이미지 복사 --> 이미지 병합하기 위함!
                beforecopy = "~/ganjyfont/results_ver2_font/" + letter + "_" + char +"_pix2pix/test_latest/images/" + str(request.user) + "_" + day_time + "_" + filename[letter] + "_fake_B.png"
                aftercopy = "./media/result/" + str(request.user) + "_" + day_time + "/" + str(i) + ".png"
                cp_command = "cp " + beforecopy + " " + aftercopy
                os.system(cp_command)
        

        
        ###### 3.이미지 이어붙이기 #####
        print("=============image merge===============")
        string = input_str

        directory = './media/result/'+ str(request.user) + "_" + day_time 
        blank = "./media/blank/blank.png"

        
        for s, i in zip(string, range(len(string))) :
            if i is 0:
                result = directory + "/" +  str(i) +'.png'
                result = cv2.imread(result, cv2.IMREAD_GRAYSCALE)
                result = cleanside(result)
                result = morph(result)
            
            elif s is " " :
                blank = "./media/blank/blank.png"
                blank = cv2.imread(blank, cv2.IMREAD_GRAYSCALE)
                result = cv2.hconcat([result, blank])
            
            else:    
                temp = directory + "/" + str(i) +'.png'
                print(temp)
                temp = cv2.imread(temp, cv2.IMREAD_GRAYSCALE)
                temp = cleanside(temp)
                temp = morph(temp)
                result = cv2.hconcat([result, temp])
                print(str(i))
        

        # 결과 이미지 경로 지정
        # 결과 이미지 webserver/Graduate/media/output 경로에 저장하기
        imgName = "./media/output/" + userTime  + "result.png"
        cv2.imwrite(imgName, result)
        
        

        
        ##### 4. 이미지 db에 저장 #####
        output_photo = "./output/" + userTime  + "result.png"
        font.output_photo1 = output_photo
        font.save(update_fields=['output_photo1']) # 데베에 저장

        return redirect('fontsapp:result', input_id=font.pk) 


    else :  #페이지 처음 들어갈 때 (GET)
        font = get_object_or_404(Font, pk=input_id)
        input_str = str(font.final_phrase) #checkpoint 있는 문자들 + * 로만 되어있는 문구

        return render(request, 'loading.html', {'font':font})

#read
@login_required
def result(request, input_id):
    ## 결과페이지 ##

    font = get_object_or_404(Font, pk=input_id)
    return render(request, 'result.html', {'font':font})
