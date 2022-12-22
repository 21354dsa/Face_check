from flask import Flask, redirect, url_for, \
                render_template, request
import os
from view.tch_app import tch_app
from view.stud_app import stud_app
from view.api_app import api_app
from models.exts import db

pjdir = os.path.abspath(os.path.dirname(__file__))

UPLOAD_FOLDER = './img/'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])

app = Flask(__name__)

app.secret_key = b'_5#y\n\xec]/2L"F4Q8z1a(*%'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024  # 16MB
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
#  設置sqlite檔案路徑
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + \
    os.path.join(pjdir, 'date.db')

#----------------導入其它網頁後端----------------
app.register_blueprint(tch_app)
app.register_blueprint(stud_app)
app.register_blueprint(api_app)

db.init_app(app)
with app.app_context():
    db.create_all()
#----------------函數----------------



#----------------網站後台----------------
@app.route('/index', methods=["POST","GET"])
@app.route("/" , methods=["POST","GET"])
def index():
    if request.method == "POST":
        if "老師" in request.values.get("send"):
            return redirect(url_for("tch_app.teacher_login"))

        else:
            return redirect(url_for("stud_app.login_stud"))
    return render_template("index.html")

if __name__ =="__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)#host="0.0.0.0", port=3000
