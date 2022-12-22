from models.exts import db
from datetime import datetime

# 建立模型物件
class Student(db.Model):
    __tablename__ = "Student"
    id = db.Column(db.String(10), primary_key=True, unique=True)
    time = db.Column(db.DateTime, default=datetime.now, nullable=False)

    def __init__(self, id, time):
        self.id=id
        self.time=time

class Teacher(db.Model):
    """ 老師ID 
		密碼(雜湊碼)	
		mail """
    __tablename__ = "Teacher"
    id = db.Column(db.String(10), primary_key=True, unique=True)
    password = db.Column(db.String(100), nullable=False)
    mail = db.Column(db.String(20), unique=True, nullable=False)
    def __init__(self, id, password, mail):
        self.id=id
        self.password=password
        self.mail=mail
    
class Teacher_To_Class(db.Model):
    __tablename__ = "Teacher_To_Class"
    id = db.Column(db.Integer, primary_key=True, unique=True)
    className = db.Column(db.String(10), unique=False, nullable=False)
    teacherId = db.Column(db.String(10), unique=False, nullable=False)
    def __init__(self, id, teacherId, className):
        self.id=id
        self.className=className
        self.teacherId=teacherId

class Class_To_Student(db.Model):
    __tablename__ = "Class_To_Student"
    pid = db.Column(db.Integer, primary_key=True)
    classid = db.Column(db.Integer, unique=False, nullable=False)
    studClass = db.Column(db.String(5), unique=False, nullable=False)
    studentId = db.Column(db.String(10), unique=False, nullable=False)
    studName = db.Column(db.String(5), unique=False, nullable=False)
    choose = db.Column(db.Boolean, nullable=False)

    def __init__(self, classid, studClass, studentId,studName, choose):
        self.classid=classid
        self.studClass=studClass
        self.studentId=studentId
        self.studName=studName
        self.choose=choose

class Student_Face(db.Model):
    __tablename__ = "Student_Face"
    pid = db.Column(db.Integer, primary_key=True)
    studentId = db.Column(db.String(10), unique=False, nullable=False)
    fileId = db.Column(db.String(10), unique=True, nullable=False)
    feature = db.Column(db.String, unique=False, nullable=False)
    def __init__(self, studentId, fileId, feature):
        self.studentId=studentId
        self.fileId=fileId
        self.feature=feature

def upload(data):
    """上傳資料到資料庫"""
    db.session.add(data)
    db.session.commit()

def updata(data):
    db.session.commit()

def delete_data(data):
    if type(data)==list:
        for i in data:
            db.session.delete(i)
    else:
        db.session.delete(data)
    db.session.commit()
# 1.建立表
