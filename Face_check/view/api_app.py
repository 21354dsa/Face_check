from flask import request, Blueprint
from models.model import Student_Face, Teacher, Class_To_Student,\
                         Teacher_To_Class, upload, updata
from view.functinos import *

api_app = Blueprint('api_app', __name__)

@api_app.route("/api/login", methods=["POST", "GET"])
def login():
    msg={}
    if request.method=="POST":
        ID=request.form["_ID"]
        password=request.form["password"]
        if ID=="" or password=="":
            msg["msg"]= "Input your ID or Password"
        query = Teacher.query.filter_by(id=ID).first()
        if not(query is None):
            
            if sha_256(password)==query.password:
                #?ªÂÖ•?êÂ?
                
                msg["msg"]= "OK" #?áÊ??∞Ë®≠ÂÆö‰???
            else:
                msg["msg"]="Password Error"
        else:
            msg["msg"]="Not ID"
    return msg


@api_app.route("/api/getClass", methods=["POST", "GET"])
def getClass():
    msg={}
    msg["msg"]=False
    msg["request"]=""
    if request.method=="POST":
        ID=request.form["_ID"]
        classquery=Teacher_To_Class.query.filter_by(teacherId=ID).all()
        if not(classquery is None):
            classList=[]
            for T_class in classquery:
                data={}
                data["number"]=T_class.id
                data["name"]=T_class.className
                classList.append(data)
            msg["request"]=classList
            msg["msg"]=True
    return msg

@api_app.route("/api/set_roll_call", methods=["POST", "GET"])
@api_app.route("/api/getStudent", methods=["POST", "GET"])
def getStudent():
    msg={}
    msg["msg"]=False
    msg["request"]=""
    if request.method=="POST":
        class_id=request.form["class_id"]
        studChooes=Class_To_Student.query.filter_by(classid=class_id).all()
        if not(studChooes is None):
            classList=[]
            for stud in studChooes:
                data={}
                data["pid"]=stud.pid
                data["studClass"]=stud.studClass
                data["studId"]=stud.studentId
                data["studName"]=stud.studName
                data["choose"]=stud.choose
                classList.append(data)
            msg["request"]=classList
            msg["msg"]=True
    return msg

@api_app.route("/api/getFeature", methods=["POST", "GET"])
def getFeature():
    msg={}
    msg["msg"]=False
    msg["request"]=[]
    if request.method=="POST":
        class_id=request.form["class_id"]
        studChooes=Class_To_Student.query.filter_by(classid=class_id).all()
        if not(studChooes is None):
            for stud in studChooes:
                stud_json={}
                features=[]
                stud_f=Student_Face.query.filter_by(studentId=stud.studentId).all()
                for feature in stud_f:
                    features.append(feature.feature)
                stud_json["studClass"]=stud.studClass
                stud_json["studentId"]=stud.studentId
                stud_json["studName"]=stud.studName
                stud_json["features"]=features
                msg["request"].append(stud_json)
            msg["msg"]=True
            #msg["request"]=features
    return msg