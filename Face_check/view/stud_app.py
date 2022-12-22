from flask import Flask, redirect, url_for, \
                render_template, request, make_response, Blueprint
from requests import delete
from models.exts import db
from models.model import Student, Class_To_Student, Teacher_To_Class,\
     upload, updata, Student_Face, delete_data
import models.face_dataset as fd
from werkzeug.utils import secure_filename
from view.functinos import *
import os
from datetime import datetime
from functools import reduce

stud_app = Blueprint('stud_app', __name__)

n=len(os.path.dirname(os.path.abspath(__file__)).split("/")[-1])

#print(os.path.dirname(os.path.abspath(__file__)).split("/"))
UPLOAD_FOLDER = "./img/"  #ubuntu要改這行  os.path.dirname(os.path.abspath(__file__))[:-n]+'/img/'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])


def allowed_file(filename):
    """檢查檔案格式
        filename:檔案名稱
    """
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

#login page
@stud_app.route("/login_stud", methods=["POST","GET"])
def login_stud():
    """登入介面"""
    msg=""
    id=""
    if request.method == "POST":

        #傳送1次性mail
        if request.values.get("send")=="Get password":      
            ID=request.form["_ID"]
            
            paword=get_code(quantity=10) #產生亂碼
            msg="請至Gmail接收一次性密碼後輸入"
            #傳送至mail
            mail(ID+"@stud.sju.edu.tw", paword, "student")
            #
            resp = make_response(render_template("student/login_stud.html", msg=msg, id=ID))#設定cookie

            resp.set_cookie("ID", ID)
            resp.set_cookie("paword_256", sha_256(paword))
            
            return resp

        #登入驗證
        elif request.values.get("send")=="login":
            ID=request.form["_ID"]
            in_pass=request.form["password"]
            h_256=request.cookies.get("paword_256")
            stud_id=request.cookies.get("ID")
            if sha_256(in_pass)==h_256 and ID==stud_id:
                #跳轉到設定資料網頁
                query = Student.query.filter_by(id=stud_id).first()
                if query is None:
                    nowTime = datetime.now()
                    student = Student(stud_id, nowTime)
                    upload(student)
                    classquery = Class_To_Student.query.filter_by(studentId=stud_id).all()
                    for i in classquery:
                        i.choose=True
                        updata(i)

                return redirect(url_for("stud_app.stud_set"))
            else:
                msg="密碼錯誤"
                id=ID

    return render_template("student/login_stud.html", id=id, msg=msg)

@stud_app.route("/stud_set", methods=["POST","GET"])
def stud_set():
    """學生設定介面"""
    try:
        stud_id=request.cookies.get("ID")
        img_path=UPLOAD_FOLDER+stud_id
    except:
        return redirect(url_for("stud_app.login_stud"))

    msg="檔案大小不可超過2MB，最多5張照片"

    #檢查資料夾是否存在  
    try:
        if not os.path.exists(img_path):
            os.mkdir(img_path)
    except Exception as  e:
        print("建立資料夾錯誤",str(e))
        msg="建立資料夾錯誤"

    #讀取舊照片
    imgsct=[]
    paths=[]

    path = img_path+"/"
    file_list=os.listdir(path)
    for i in file_list:
        imgsct.append(img_to_b64(path+i))
        paths.append(path+i)

    #顯示已經登入的課程
    studclass=Class_To_Student.query.filter_by(studentId=stud_id).all()
    table_display=not(studclass is None)
    classdata=[]
    if table_display:
        for stud in studclass:
            data={}
            query=Teacher_To_Class.query.filter_by(id=stud.classid).first()
            data["classId"]=query.id
            data["className"]=query.className
            classdata.append(data)

    if request.method == 'POST':

        #刪除照片
        if request.values.get("send")=="delete":       
            del_img=request.values.get("filename")
            fileId=del_img.split('/')[-1].split('.')[0]
            rmFacePix=Student_Face.query.filter_by(fileId=fileId).first()
            delete_data(rmFacePix)
            os.remove(del_img)
            return redirect(url_for("stud_app.stud_set"))
        
        #上傳照片
        elif request.values.get("send")=="upload":      
            uploaded_files = request.files.getlist("file[]")
            file_num=len(os.listdir(path))
            for file in uploaded_files:
                if file and allowed_file(file.filename) and file_num<5:
                    
                    filetype = secure_filename(file.filename).split(".")[1]
                    fileId=get_code(6)    
                    while not(Student_Face.query.filter_by(fileId=fileId).first() is None):
                        fileId=get_code(6)
                    save_path=os.path.join(img_path, fileId+"."+filetype)
                    file.save(save_path)
                    print(save_path)
                    feature=fd.face_feature(save_path)
                    if ( feature == [] ):
                        os.remove(save_path)
                    else:
                        str_feature=reduce(lambda x, y: x+";"+y, feature.astype('str'))
                        stud_fature=Student_Face(stud_id, fileId, str_feature)
                        print(stud_fature, stud_id, fileId)
                        upload(stud_fature)
                    file_num+=1

            return redirect(url_for("stud_app.stud_set"))
            
    return render_template("student/stud_set.html", _ID=stud_id, FileAndName=zip(imgsct, paths), msg=msg,
                            table_display=table_display, studclass=classdata)
