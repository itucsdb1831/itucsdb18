from flask import Flask, render_template, request, redirect, url_for
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from user import User
from passlib.hash import pbkdf2_sha256 as hasher
import database as db
from game import Game
import views

# from database import get_user

app = Flask(__name__)
app.config.from_object("settings")
app.secret_key = b'\xfa\r\xad<\xc8s\x08\xc7\xa4\x9f!\xb7Rz\\\x86'

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
    return render_template("signupresult.html", successful=successful)

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
def home_page():
    return render_template("home.html")

@app.route("/profile/")
@login_required
def profile():
    return render_template("profile.html", user_name=current_user.get_user_name())

@app.route("/logout/")
@login_required
def logout():
    logout_user()
    return redirect(url_for("home_page"))

# -----------------------------------------------------------------------


@app.route("/store")
def store_page():
    games = db.get_games()
    return render_template("store.html", games=games)


@app.route("/store/<int:game_id>")
def game_page(game_id):
    game = db.get_game(game_id)
    return render_template("game.html", game=game)


@app.route("/game_add", methods=['GET', 'POST'])
def game_add_page():
    if request.method == "GET":
        return render_template("game_add.html")
    else:
        form_title = request.form["title"]
        form_genre = request.form["genre"]
        form_age_restriction = request.form["age_restriction"]
        form_price = request.form["price"]
        game = Game(None, form_title, form_genre, 0, 0, form_age_restriction, form_price)
        db.add_game(game)
        return redirect(url_for("game_add_page_result_page"))


@app.route("/game_add_result")
def game_add_page_result_page():
    return render_template("game_add_result.html")


@app.route("/store/<int:game_id>/game_rate", methods=['GET', 'POST'])
def game_rate_page(game_id):
    if request.method == "GET":
        return render_template("game_rate.html")
    else:
        form_rating = request.form["rating"]
        db.update_rating_of_game(game_id, form_rating)
        return redirect(url_for("game_rate_page_result_page"))


@app.route("/store/game_rate_result")
def game_rate_page_result_page():
    return render_template("game_rate_result.html")


if __name__ == "__main__":
    app.run()