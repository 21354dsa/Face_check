from http.cookiejar import Cookie
from flask import Flask, redirect, url_for, session,\
                render_template, request, make_response, Blueprint
from view.functinos import *
from models.exts import db
from models.model import *
import pandas as pd
#import database

tch_app = Blueprint('tch_app', __name__)


def allowed_file(filename):
    """檢查檔案格式
        filename:檔案名稱
    """
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in "xlsx"


@tch_app.route("/teacher_signup", methods=["POST", "GET"])
def teacher_signup():
    if request.method=="POST":

        if request.values.get("send")=="傳送驗證碼":  
            #print("傳送驗證碼")    
            ID=request.form["_ID"]
            password=request.form["password"]
            captcha=get_code(quantity=10) #產生亂碼
            if ID=="" or password=="":
                return render_template("teacher/tch_signup.html", msg="請輸入帳號或密碼", id=ID)

            #傳送至mail
            mail(ID+"@mail.sju.edu.tw", captcha, "teacher") #-----------------------------------正式上線要改
            #
            resp = make_response(render_template("teacher/tch_signup.html", msg="請輸入驗證碼", id=ID))#設定cookie
            
            resp.set_cookie("ID", ID)
            resp.set_cookie("password", sha_256(password))
            resp.set_cookie("captcha", sha_256(captcha))
            
            return resp

        #註冊驗證
        elif request.values.get("send")=="sign up":
            ID=request.form["_ID"]
            password=request.form["password"]
            captcha=request.form["captcha"]

            password_256=request.cookies.get("password")
            captcha_256=request.cookies.get("captcha")
            cookie_ID=request.cookies.get("ID")
            if sha_256(captcha)==captcha_256 and ID==cookie_ID and sha_256(password)==password_256:
                #跳轉到設定資料網頁
                query = Teacher.query.filter_by(id=cookie_ID).first()
                if query is None:
                    teacher = Teacher(ID, password_256, ID+"@mail.sju.edu.tw")#-----------------------------------正式上線要改
                    upload(teacher)
                    
                return redirect(url_for("tch_app.teacher_login"))
            else:
                msg=""
                if ID!=cookie_ID:
                    msg+="帳號"
                if sha_256(password)!=password_256:
                    msg+="密碼"
                if sha_256(captcha)!=captcha_256:
                    msg+="驗證碼"
                return render_template("teacher/tch_signup.html", msg=msg+"錯誤")

    return render_template("teacher/tch_signup.html")


@tch_app.route("/teacher_login", methods=["POST", "GET"])
def teacher_login():
    msg=""
    if request.method=="POST":
        
        if request.values.get("send") == "login":
            ID=request.form["_ID"]
            password=request.form["password"]
            if ID=="" or password=="":
                return render_template("teacher/tch_signup.html", msg="請輸入帳號或密碼", id=ID)
            query = Teacher.query.filter_by(id=ID).first()
            if not(query is None):
                if sha_256(password)==query.password:
                    #登入成功
                    resp = make_response(redirect(url_for("tch_app.teacher_set")))#設定cookie
                    session["msg"]=""
                    resp.set_cookie("ID", ID)
                    resp.set_cookie("password", sha_256(password))

                    return resp #切換到設定介面
                else:
                    msg="密碼錯誤"
            else:
                msg="尚未註冊"
        else:
            #切換到註冊介面
            return redirect(url_for("tch_app.teacher_signup"))

    return render_template("teacher/tch_login.html", msg=msg)



@tch_app.route("/teacher_set", methods=["POST", "GET"])
def teacher_set(): 
    table_display=False
    studChooes=[]
    updata_msg=session.get("msg")
    tchId=request.cookies.get("ID")
    classquery=Teacher_To_Class.query.filter_by(teacherId=tchId).all()
    if request.method=="POST":
        if request.form["Do"]=="updata_class":
            classNumber=request.form["classNumber"]
            className=request.form["className"]
            file = request.files['__file']
            if classNumber=="" or className=="" :
                session["msg"]="課程名編號與名稱不可為空"
                
            elif file and allowed_file(file.filename):
                print("上傳課程資料")
                #上傳教師的課程到資料庫
                tch_class=Teacher_To_Class(classNumber, tchId, className)
                upload(tch_class)

                #讀取選課學生資料
                data_xls = pd.read_excel(file)
                for df in data_xls.values:
                    query = Student.query.filter_by(id=df[1]).first()
                    class_stud=Class_To_Student(classNumber,df[0] ,df[1] , df[2], not(query is None))
                    upload(class_stud)
                session["msg"]="上傳完畢"
                return redirect(url_for("tch_app.teacher_set"))
            else:
                session["msg"]="檔案不可為空"

    elif request.method=="GET":        
        session["msg"]=""
        val=request.args.get("send")
        classid = request.args.get('select')
        studChooes=Class_To_Student.query.filter_by(classid=classid).all()
        if val=="搜尋":
            table_display=True
        elif val=="刪除":
            table_display=False
            delete_data(studChooes)
            tch_class=Teacher_To_Class.query.filter_by(id=classid).first()
            delete_data(tch_class)
            return redirect(url_for("tch_app.teacher_set"))

    return render_template("teacher/tch_set.html", _ID=tchId, updata_msg=updata_msg, classNames=classquery, 
                            table_display=table_display, studchooes=studChooes)