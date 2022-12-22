from email.mime import multipart
import hashlib
import string
import random
import base64



def mail(to_b,passcode,who):
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText
    #建立訊息物件
    msg=MIMEMultipart()
    #利用物件建立基本設定
    
    from_a="108406011@stud.sju.edu.tw"
    msg["Subject"]="臉部識別點名系統"
    msg["From"]=from_a
    msg["To"]=to_b
    

    #寄送郵件主要內容
    #msg.set_content("測試郵件純文字內容") #純文字信件內容
    if "stud" in who:  #學生
        msg.attach(MIMEText("<h2>臉部識別點名系統</h2>\
                            您的一次性登入密碼為<br><h3>"+\
                            passcode+"</h3>", _subtype="html")) #HTML信件內容
    else:               #教師
        msg.attach(MIMEText("<h2>臉部識別點名系統</h2>\
                            您的驗證碼為<br><h3>"+\
                            passcode+"</h3>", _subtype="html")) #HTML信件內容

    acc="project.test.22645@gmail.com"
    password="eszgezutnqucqdno"

    #連線到SMTP Sevver
    import smtplib
    #可以從網路上找到主機名稱和連線埠
    server=smtplib.SMTP_SSL("smtp.gmail.com",465) #建立gmail連驗
    server.login(acc,password)
    server.send_message(msg)
    server.quit() #發送完成後關閉連線

def get_code(quantity):
    """
    生產亂碼
    quantity:需要的數量
    """
    return ''.join(random.sample(string.ascii_letters + string.digits , quantity))

def sha_256(string):
    return(hashlib.sha256(string.encode('utf-8')).hexdigest())

def img_to_b64(img_paht):
    """
        圖檔轉base64
        img_paht:圖檔位置
    """
    img_stream=""
    with open(img_paht, 'rb') as img_f:
        img_stream = img_f.read()
        img_stream = base64.b64encode(img_stream).decode()
        #print(img_stream)
    return img_stream
