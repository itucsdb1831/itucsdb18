from flask import Flask, render_template, request, redirect, url_for
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from user import User
from passlib.hash import pbkdf2_sha256 as hasher
import database as db
from game import Game
from review import Review
from item import Item

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
        db.insert_user(User(form_name, hasher.hash(form_pw), True, False, 0))
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
                games_of_user = db.get_games_of_user(current_user.id)
                friend_requests = db.get_friend_requests(current_user.id)
                friends = db.get_friends(current_user.id)
                return render_template('profile.html', user=current_user, games_of_user=games_of_user,
                                       friend_requests=friend_requests, friends=friends)
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
    games_of_user = db.get_games_of_user(current_user.id)
    friend_requests = db.get_friend_requests(current_user.id)
    friends = db.get_friends(current_user.id)
    return render_template("profile.html", user=current_user, games_of_user=games_of_user,
                           friend_requests=friend_requests, friends=friends)


@app.route("/logout/")
@login_required
def logout():
    logout_user()
    return redirect(url_for("home_page"))


@app.route("/store/<int:game_id>/add_review/", methods=["GET", "POST"])
@login_required
def add_review(game_id):
    if request.method == "POST":
        db.insert_review(Review(current_user.id, game_id, request.form.get("label"), request.form.get("content")))
        return redirect(url_for('game_page', game_id=game_id))
    else:
        return render_template("add_review.html", game=db.get_game(game_id))

# -----------------------------------------------------------------------


@app.route("/store", methods=['GET', 'POST'])
def store_page():
    if request.method == "GET":
        games = db.get_games()
        return render_template("store.html", games=games)
    else:
        form_game_ids = request.form.getlist("game_ids")
        for form_game_id in form_game_ids:
            db.delete_game(int(form_game_id))
        return redirect(url_for("store_page"))


@app.route("/store/<int:game_id>", methods=['GET', 'POST'])
def game_page(game_id):
    if request.method == 'POST':
        form_item_ids = request.form.getlist("item_ids")
        for form_item_id in form_item_ids:
            db.delete_item(int(form_item_id))
        return redirect(url_for("game_page", game_id=game_id))

    game = db.get_game(game_id)
    items = db.get_items(game_id)
    reviews = db.get_reviews4game(game_id)
    return render_template("game.html", game=game, items=items, reviews=reviews)


@app.route("/game_add", methods=['GET', 'POST'])
@login_required
def game_add_page():
    if not current_user.is_admin:
        return render_template('not_allowed.html')
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


@app.route("/store/<int:game_id>/item_add", methods=['GET', 'POST'])
def item_add_page(game_id):
    if request.method == 'GET':
        return render_template("item_add.html")

    form_name = request.form["name"]
    form_rarity = request.form["rarity"]
    form_level = request.form["level"]
    item = Item(None, game_id, form_name, form_rarity, form_level)
    db.add_item(item)
    return render_template("item_add_result.html", game_id=game_id)


@app.route("/game_add_result")
@login_required
def game_add_page_result_page():
    if not current_user.is_admin:
        return render_template('not_allowed.html')
    return render_template("game_add_result.html")


@app.route("/store/<int:game_id>/game_rate", methods=['GET', 'POST'])
@login_required
def game_rate_page(game_id):
    if request.method == "GET":
        return render_template("game_rate.html")
    else:
        form_rating = request.form["rating"]
        db.update_rating_of_game(game_id, form_rating)
        return redirect(url_for("game_rate_page_result_page"))


@app.route("/store/game_rate_result")
@login_required
def game_rate_page_result_page():
    return render_template("game_rate_result.html")


@app.route("/store/<int:game_id>/game_purchase")
@login_required
def game_purchase_page(game_id):
    game = db.get_game(game_id)
    return render_template("game_purchase.html", game=game)


@app.route("/store/<int:game_id>/game_purchase_result")
@login_required
def game_purchase_result_page(game_id):
    game = db.get_game(game_id)
    success = False
    if current_user.is_admin or current_user.balance >= game.price:
        success = db.add_game_to_user(game.game_id, current_user.id)
        if success:
            db.decrease_balance_of_user(current_user.id, game.price)
    return render_template("game_purchase_result.html", game=game, success=success)


@app.route("/profile/code_enter", methods=['GET', 'POST'])
@login_required
def code_enter_page():
    if request.method == "GET":
        return render_template("code_enter.html")
    else:
        form_code = request.form["code"]
        valid = db.check_code(form_code)
        if valid:
            db.add_balance_to_user(current_user.id)
        return render_template("code_enter_result.html", valid=valid)

# -----------------------------------------------------------------------


@app.route("/profile/<int:user_id_to_add>", methods=['GET', 'POST'])
@login_required
def friend_request_page(user_id_to_add):
    if request.method == "GET":
        return render_template("friend_request.html", user_to_add=user_id_to_add)
    else:
        accepted = False
        form_decision = request.form["decision"]
        if form_decision == "Accept":
            accepted = True
            db.add_friend(current_user.id, user_id_to_add)
        db.remove_request(user_id_to_add, current_user.id)
        return render_template("friend_request_result.html", accepted=accepted, user_added=user_id_to_add)


@app.route("/profile/friend_add", methods=['GET', 'POST'])
@login_required
def friend_add_page():
    if request.method == "GET":
        return render_template("friend_add.html")
    else:
        form_user_name = request.form["user_name"]
        user_id_to = db.get_user_id(form_user_name)
        valid = False
        are_friends = False
        is_self = False
        if user_id_to is not None:
            valid = True
            are_friends = db.check_if_already_friends(current_user.id, user_id_to)
            if not are_friends:
                if current_user.id != user_id_to:
                    db.send_friend_request(current_user.id, user_id_to)
                else:
                    is_self = True
        return render_template("friend_add_result.html", valid=valid, are_friends=are_friends, is_self=is_self,
                               user_to=user_id_to)


if __name__ == "__main__":
    app.run()
