from flask import Flask, render_template, request, redirect, url_for
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from user import User
from passlib.hash import pbkdf2_sha256 as hasher
import database as db

#from database import get_user

app = Flask(__name__)
app.config.from_object("settings")
app.secret_key = b'\xfa\r\xad<\xc8s\x08\xc7\xa4\x9f!\xb7Rz\\\x86'
app.config["DEBUG"] = True

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return db.get_user(user_id)

@app.route("/signupresult/", methods=["POST"])
def sign_up_result():
    form_name = request.form.get("user_name")
    form_pw = request.form.get("password")
    name_is_dupl = db.query_user_name(form_name)
    successful = False
    if db.query_user_name(form_name) == None:
        db.insert_user(User(form_name, hasher.hash(form_pw)))
        successful = True
    return render_template("signupresult.html", successful = successful)

@app.route('/login/', methods=['GET', 'POST'])
def login():

    if request.method == "POST":
        user = db.query_user_name(request.form.get("user_name"))
        if user:
            if hasher.verify(request.form.get("password"), user.get_pw()):
                login_user(user)
                next = request.args.get('next')
                
                return "logged in"
    return render_template('login.html')

@app.route("/signup/")
def signup():
    return render_template("signup.html")

@app.route("/")
def homepage():
    return render_template("homepage.html")

@app.route("/profile/")
@login_required
def profile():
    return render_template("profile.html", user_name = current_user.get_user_name())

@app.route("/logout/")
@login_required
def logout():
    logout_user()
    return redirect(url_for("homepage"))


# -----------------------------------------------------------------------

@app.route("/store/")
def store():
    return render_template("store.html")

if __name__ == "__main__":
    app.run()