import imutils
import numpy as np
import cv2
import os
from deepface import DeepFace
import dlib
from imutils import face_utils
#from tensorflow.keras.models import model_from_json, load_model
#
#
detector_D = dlib.get_frontal_face_detector()

""" this_path=os.path.dirname(os.path.abspath(__file__))
print(this_path)
model = load_model("./models/Facenet512.h5")
json_file = open(this_path+"/Facenet512.json", 'r')
loaded_model_json = json_file.read()
json_file.close()
model = model_from_json(loaded_model_json)
model.load_weights(this_path+"/Facenet512_weights.h5") """

#偵測人臉
def getFaces_dlib(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = detector_D(gray,0)
    for face in faces:
        (x, y, w, h) = face_utils.rect_to_bb(face)
        cv2.rectangle(gray, (x, y), (x + w, y + h), (255, 0, 0), 3)
        return [img[y:y+h,x:x+w]]

    return []

#辨識人臉特徵點
def face_feature (filename):
    model = DeepFace.build_model("Facenet512")
    img = cv2.imread(filename)      #讀檔
    faces = getFaces_dlib(img)  
    for face in faces:
        face_img=imutils.resize(face, 160, 160)         #調成模型輸入大小
        while face_img.shape < (160,160,3):
            n=np.zeros((1,160,3))
            face_img=np.append(face_img , n, axis=0)
        while face_img.shape > (160,160,3):
            face_img=np.delete(face_img , [-1], axis=0)
        face_img=face_img.astype(np.float64)/255        #正規化
        samples  =  np.expand_dims(face_img,  axis=0)   
        print(samples)
        
        feature  =  model.predict(samples)
        return feature[0]
    return []


if __name__=="__main__":

    fliename="../people/"           #人臉圖檔位置
    file_list=os.listdir(fliename)

    data_out={}
    for i in file_list:
        file_path=fliename+i
        if not os.path.isdir(file_path): #檢查是否為資料夾
            continue
        print(file_path)
        data_out[i]=[]
        for name in os.listdir(file_path):
            feature=face_feature(file_path+"/"+name)
            try:
                if (feature==None):
                    continue
            except:
                pass
            data_out[i].append(feature)
        data_out[i]=np.array(data_out[i])
    np.save("feature",data_out)

    load_dict = np.load('./feature.npy',allow_pickle=True).item()

