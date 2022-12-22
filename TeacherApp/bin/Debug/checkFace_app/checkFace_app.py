from turtle import delay
from flask import Flask, redirect, url_for, \
                render_template, request
import os
import imutils
import numpy as np
import cv2
import dlib
from imutils import face_utils
#from deepface import DeepFace
from tensorflow.keras.models import load_model
import time
import sys
import json

detector = dlib.get_frontal_face_detector() #建立人臉辨識器

exe_name=sys.executable.split("\\")[-1]
exe_path=sys.executable[:-len(exe_name)]#取到執行檔的位置
this_path="\\".join(sys.executable.split("\\")[:-2])#取到執行檔的位置

from tensorflow.keras.models import model_from_json

try: #打包成EXE使用
    json_file = open(exe_path+"\\model\\Facenet512.json", 'r')
    loaded_model_json = json_file.read()
    json_file.close()
    model = model_from_json(loaded_model_json)
    model.load_weights(exe_path+"\\model\\Facenet512_weights.h5")

except:#本地測時使用
    json_file = open(r"D:\University\project\my\Vggface\Facenet512.json", 'r')
    loaded_model_json = json_file.read()
    json_file.close()
    model = model_from_json(loaded_model_json)
    model.load_weights(r"D:\University\project\my\Vggface\Facenet512_weights.h5")


app = Flask(__name__)
back=False
load_features={}#{"學號":[特徵,特徵]}
present=""
absent=[]
numToName={}

#----------------函數----------------

def cosine(feature1, feature2):
    return 1 - (np.dot(feature1, feature2)/(np.linalg.norm(feature1)*np.linalg.norm(feature2)))

#人臉辨識
def face_check(img_RGB, x, y, w, h):
    global load_features
    face_name="None"
    face_num=99
    try:
        face_img=img_RGB[y:y+h,x:x+w]
        face_img=imutils.resize(face_img,160,160)
        while face_img.shape < (160,160,3):
            n=np.zeros((1,160,3))
            face_img=np.append(face_img , n, axis=0)
        while face_img.shape > (160,160,3):
            face_img=np.delete(face_img , [-1], axis=0)
        face_img=face_img.astype(np.float64)/255
        samples  =  np.expand_dims(face_img,  axis=0)
        feature  =  model.predict(samples)[0]
        for key, val in load_features.items():
            for i in val:
                d1=cosine(feature,i)
                if d1<face_num and d1<0.3:
                    face_num=d1
                    face_name=key
    except:
        pass

    return face_name, face_num

from PIL import Image, ImageDraw, ImageFont

def cv2ImgAddText(img, text, left, top, textColor=(0, 255, 0), textSize=30):
    if (isinstance(img, np.ndarray)):  #判斷是否OpenCV圖片類型
        img = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(img)
    fontText = ImageFont.truetype(
        "font/simsun.ttc", textSize, encoding="utf-8")
    draw.text((left, top), text, textColor, font=fontText)
    return cv2.cvtColor(np.asarray(img), cv2.COLOR_RGB2BGR)

def camera_128(cam=0):
    print(cam)
    global present
    camera = cv2.VideoCapture(cam, cv2.CAP_DSHOW) #建立鏡頭
    FPS = 24.0
    camera.set(cv2.CAP_PROP_FPS, FPS)
    start_time=time.time()
    counter=0
    old_face_name=""
    who=0
    present=""
    while True:
        global back, absent
        grabbed, img = camera.read()
        print(back, type(img))
        
        #-----------------------FPS--------------------
        fps=camera.get(cv2.CAP_PROP_FPS)
        counter +=1
        if(time.time()-start_time)!=0:
            cv2.putText(img,"FPS{0}".format(float("%.1f" %(counter/(time.time()-start_time)))),(50,50),
            cv2.FONT_HERSHEY_SIMPLEX,1,(0,0,255),3)
            counter=0
            start_time=time.time()
        time.sleep(1/fps)

        #----------------------------------------------
        img_G = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = detector(img_G, 0)
        X,Y=0,0
        wight,hight=0,0
        color=(255, 0, 0)
        for face in faces:
            x,y,w,h=face_utils.rect_to_bb(face)
            if (wight*hight<w*h):
                X, Y=x, y
                wight, hight=w, h

        
        if len(faces) != 0:
            face_name, face_num =face_check(img, X, Y, wight, hight)
            if (old_face_name==face_name and face_name!="None"):
                who+=1
            else:
                who=0
            if who>3 and face_name in absent:
                present+=face_name+";"
                absent.remove(face_name)
                who=0
                try:
                    with open(this_path+"\\list.txt", "w") as f:
                        f.write(present)
                        #print(present)
                except:
                    pass
            if face_name in present:
                color=(0, 255, 0)
            name="無選此課程"
            if face_name != "None":
                name=numToName[face_name]
            cv2.rectangle(img, (X, Y), (X + wight, Y + hight), color, 3)
            cv2.rectangle(img, (50, 80), (200, 130), (255,255,255), -1)
            img=cv2ImgAddText(img,name, 50, 80, (0,0,255))
            
            old_face_name=face_name

        cv2.imshow("face",img)
        key = cv2.waitKey(1)
        # q鍵跳出循環
        if key == ord("q") or back: #讀到檔案寫跳出
            camera.release()
            time.sleep(0.1)
            cv2.destroyAllWindows()
            time.sleep(0.2)
            return ""
    

def f_strToarray(feature_list):
    features=[]
    for str_feature in feature_list:
        f_str_list=str_feature.split(";")
        np_f=np.asarray(f_str_list, dtype=np.float32)
        features.append(np_f)
    return features
#----------------網站後台----------------

@app.route("/checkExe", methods=["POST","GET"])
def checkExe():
    return {"bool" : True}

@app.route("/OpenCamera" , methods=["POST","GET"])
def OpenCamera():
    global load_features, present, absent
    load_features={}
    msg=""
    if request.method=="GET":
        global back
        val=request.args.get("send")
        #print(val)
        if val=="1":
            back=True
        elif val=="0":
            back=False
            msg=camera_128()
    if request.method == "POST":
        if bool(request.form["Camera"]):
            stud_data=""
            with open(this_path+"\\list.txt", "w") as f:#
                f.write("")
            with open(this_path +"\\stud_data.txt", "r", encoding="utf-8") as f:#this_path+
                stud_data=f.read().encode().decode('utf-8-sig')
            response=json.loads(stud_data)

            for stud in response:
                load_features[stud["studentId"]]=f_strToarray(stud["features"])
                numToName[stud["studentId"]]=stud["studName"]
                absent.append(stud["studentId"])
            back=False
            try:
                msg=camera_128(int(request.form["webcamNumber"]))
            except :
                msg="錯誤"
        else:
            back=True

    return {"msg" : msg}

if __name__ =="__main__":
    app.run(port=3000, debug=True, threaded=True)#host="0.0.0.0", port=3000