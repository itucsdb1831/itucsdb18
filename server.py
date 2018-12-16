from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_uploads import UploadSet, configure_uploads, IMAGES
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from user import User
from passlib.hash import pbkdf2_sha256 as hasher
from database import Database
from game import Game
from review import Review
from item import Item
from screenshot import Screenshot
from profile_photo import ProfilePhoto
from datetime import datetime
from os import remove, path


def select_timestamp_for_sort(element):
    return element[3]


with open("dsn.txt") as file:
    dsn = file.read()

db = Database(dsn)

app = Flask(__name__)
app.config.from_object("settings")
app.secret_key = b'\xfa\r\xad<\xc8s\x08\xc7\xa4\x9f!\xb7Rz\\\x86'

images = UploadSet("images", IMAGES)
img_source = 'static/img'
app.config['UPLOADED_IMAGES_DEST'] = img_source
configure_uploads(app, images)

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
    is_successful = db.query_user_name(form_name) is None
    if is_successful:
        db.insert_user(User(form_name, hasher.hash(form_pw), True, False, 0))
        user_id = db.get_user_id(form_name)
        db.initialize_profile_photo(user_id)
    return render_template("signupresult.html", successful=is_successful)


@app.route('/login/', methods=['GET', 'POST'])
def login():

    if request.method == "POST":
        user = db.query_user_name(request.form.get("user_name"))
        if user:
            if hasher.verify(request.form.get("password"), user.get_pw()):
                login_user(user)
                next = request.args.get('next')
                return redirect(url_for("profile", user_id = current_user.id))
    return render_template('login.html')


@app.route("/signup/")
def signup():
    return render_template("signup.html")


@app.route("/")
def home_page():
    return render_template("home.html")


@app.route("/profile/<int:user_id>/", methods=["GET", "POST"])
@login_required
def profile(user_id):
    if request.method == "POST":
        form_item_id = request.form["item_id"]
        db.delete_item_from_user(form_item_id, user_id)
        return redirect(url_for("profile", user_id=user_id))

    profile_photo_name = db.get_profile_photo_of_user(user_id)
    games_of_user = db.get_games_of_user(user_id)
    items_of_user = db.get_items_of_user(user_id)
    screenshots = db.get_screenshots_of_user(user_id, current_user.id)
    reviews = db.get_reviews_of_user(user_id, current_user.id)
    if user_id == current_user.id:
        received_friend_requests = db.get_received_friend_requests(current_user.id)
        sent_friend_requests = db.get_sent_friend_requests(current_user.id)
        friends = db.get_friends(current_user.id)
    else:
        received_friend_requests = []
        sent_friend_requests = []
        friends = []
    return render_template("profile.html", user=db.get_user(user_id), games_of_user=games_of_user,
                           received_friend_requests=received_friend_requests,
                           sent_friend_requests=sent_friend_requests, friends=friends, items_of_user=items_of_user,
                           screenshots=screenshots, images=images, reviews=reviews,
                           profile_photo_name=profile_photo_name)


@app.route("/logout/")
@login_required
def logout():
    logout_user()
    return redirect(url_for("home_page"))


@app.route("/store/<int:game_id>/add_review/", methods=["GET", "POST"])
@login_required
def add_review(game_id):
    prev_review = db.get_prev_review(game_id, current_user.id)
    duplicate = len(prev_review) != 0
    if request.method == "POST":
        if duplicate:
            db.update_review(prev_review[0].id, request.form.get("label"), request.form.get("content"), str(datetime.utcnow()))
        else:
            db.insert_review(Review(current_user.id, game_id, request.form.get("label"), str(datetime.utcnow()), request.form.get("content")))
        return redirect(url_for('game_page', game_id=game_id))
    if duplicate:
        return render_template("add_review.html", game=db.get_game(game_id), review=prev_review[0])
    else:
        return render_template("add_review.html", game=db.get_game(game_id), review=None)


@app.route("/delete_review/", methods=["POST"])
@login_required
def delete_review():
    db.delete_review(request.form.get("review_id"))
    return redirect(url_for('game_page', game_id=request.form.get("game_id")))


@app.route("/delete_screenshot/", methods=["POST"])
@login_required
def delete_screenshot():
    db.delete_screenshot(request.form.get("shot_name"))
    if path.exists(images.path(request.form.get("shot_name"))):
        remove(images.path(request.form.get("shot_name")))
    return redirect(url_for('game_page', game_id=request.form.get("game_id")))


@app.route("/process_likes_dislikes/", methods=["POST"])
@login_required
def process_likes_dislikes():
    entities = ["REVIEWS", "SCREENSHOTS"]
    if request.form.get("sit4process") == "like":
        if request.form.get("like_sit") == "Like":
            if request.form.get("entity_type") in entities:
                db.add_like(request.form.get("entity_id"), current_user.id, request.form.get("entity_type"))
        if request.form.get("like_sit") == "You Liked It":
            if request.form.get("entity_type") in entities:
                db.remove_like(request.form.get("entity_id"), current_user.id, request.form.get("entity_type"))
    if request.form.get("sit4process") == "dislike":
        if request.form.get("disl_sit") == "Dislike":
            if request.form.get("entity_type") in entities:
                db.add_dislike(request.form.get("entity_id"), current_user.id, request.form.get("entity_type"))
        if request.form.get("disl_sit") == "You Disliked It":
            if request.form.get("entity_type") in entities:
                db.remove_dislike(request.form.get("entity_id"), current_user.id, request.form.get("entity_type"))
    return jsonify({"success": True})


@app.route("/profile/<int:user_id>/upload_profile_photo", methods=["GET", "POST"])
@login_required
def upload_profile_photo_page(user_id):
    if request.method == "GET":
        return render_template("upload_profile_photo.html", user_id=user_id)

    profile_photo = request.files["profile_photo"]
    valid_extentions = [".jpg", ".png"]

    if profile_photo.filename[len(profile_photo.filename) - 4:] in valid_extentions:
        profile_photo_name = images.save(profile_photo)
        db.change_profile_photo(ProfilePhoto(profile_photo_name, user_id))

    return redirect(url_for("profile", user_id=user_id))


@app.route("/store/<int:game_id>/add_screenshot/", methods=["GET", "POST"])
@login_required
def add_screenshot(game_id):
    if request.method == "GET":
        return render_template("add_screenshot.html", game=db.get_game(game_id))
    if "img" in request.files:
        img = request.files["img"]
        valid_ext = [".jpg", ".png"]
        img_name = None
        if img.filename[len(img.filename)-4:] in valid_ext:
            img_name = images.save(img)
            db.insert_screenshot(Screenshot(img_name,current_user.id,game_id,request.form.get("caption"),str(datetime.utcnow())))
            return render_template("add_screenshot_result.html", success=True, img_name=img_name, game_id=game_id)
        else:
            return render_template("add_screenshot_result.html", success=False, img_name=img_name, game_id=game_id)


@app.route("/store/<int:game_id>/screenshot/<int:shot_id>/", methods=["GET", "POST"])
@login_required
def screenshot(game_id, shot_id):
    if request.method == "POST":
        comment_id_to_delete = request.form.get("delete-button")
        is_getting_deleted = comment_id_to_delete is not None
        if is_getting_deleted:
            db.delete_screenshot_comment(comment_id_to_delete)
        else:
            form_content = request.form["content"]
            form_reaction = request.form["reaction"]
            form_font_size = request.form["font_size"]
            form_color = request.form["color"]
            db.add_screenshot_comment(current_user.id, game_id, shot_id,
                                      form_content, form_reaction, form_font_size, form_color)
        return redirect(url_for("screenshot", game_id=game_id, shot_id=shot_id))

    screenshot_comments = db.get_screenshot_comments(game_id, shot_id)
    return render_template("screenshot.html", shot=db.get_screenshot(shot_id), images=images,
                           screenshot_comments=screenshot_comments)

# -----------------------------------------------------------------------


@app.route("/store", methods=['GET', 'POST'])
def store_page():
    if request.method == "GET":
        games = db.get_games()
        return render_template("store.html", games=games)
    form_game_ids = request.form.getlist("game_ids")
    for form_game_id in form_game_ids:
        db.delete_game(int(form_game_id))
    return redirect(url_for("store_page"))


@app.route("/community", methods=['GET'])
@login_required
def community_page():
    not_blocked_friends_of_user = db.get_all_not_blocked_friends_for_community(current_user.id)

    reviews = []
    screenshots = []

    reviews += db.get_all_reviews_of_user_for_community(current_user.id)
    screenshots += db.get_all_screenshots_of_user_for_community(current_user.id)
    for friend_id in not_blocked_friends_of_user:
        reviews += db.get_all_reviews_of_user_for_community(friend_id)
        screenshots += db.get_all_screenshots_of_user_for_community(friend_id)

    reviews.sort(key=select_timestamp_for_sort, reverse=True)
    screenshots.sort(key=select_timestamp_for_sort, reverse=True)

    return render_template("community.html", reviews=reviews, screenshots=screenshots, images=images)


@app.route("/store/<int:game_id>", methods=['GET', 'POST'])
def game_page(game_id):
    if request.method == 'POST':
        form_item_ids = request.form.getlist("item_ids")
        for form_item_id in form_item_ids:
            db.delete_item(int(form_item_id))
        return redirect(url_for("game_page", game_id=game_id))

    game = db.get_game(game_id)
    items = db.get_items(game_id)
    reviews = []
    screenshots = []
    if current_user.is_authenticated:
        reviews = db.get_reviews_of_game(game_id, current_user.id)
        screenshots = db.get_screenshots_of_game(game_id, current_user.id)
    return render_template("game.html", game=game, items=items, reviews=reviews, screenshots=screenshots, images=images)


@app.route("/game_add", methods=['GET', 'POST'])
@login_required
def game_add_page():
    if not current_user.is_admin:
        return render_template('not_allowed.html')

    if request.method == "POST":
        form_title = request.form["title"]
        form_genre = request.form["genre"]
        form_age_restriction = request.form["age_restriction"]
        form_price = request.form["price"]
        game = Game(None, form_title, form_genre, 0, 0, form_age_restriction, form_price)
        db.add_game(game)
        return redirect(url_for("game_add_page_result_page"))
    return render_template("game_add.html")


@app.route("/store/<int:game_id>/item_add", methods=['GET', 'POST'])
@login_required
def item_add_page(game_id):
    if request.method == 'POST':
        try:
            file_picture = request.files["picture"]
            uploaded_picture = images.save(file_picture)
            form_name = request.form["name"]
            form_item_type = request.form["item_type"]
            form_rarity = request.form["rarity"]
            form_price = request.form["price"]
            item = Item(None, game_id, uploaded_picture, form_name, form_item_type, form_rarity, form_price)
            db.add_item(item)
            return render_template("item_add_result.html", game_id=game_id)
        except Exception:
            return redirect(url_for("item_add_page", game_id=game_id))
    return render_template("item_add.html")


@app.route("/store/<int:game_id>/<int:item_id>/item_update", methods=['GET', 'POST'])
@login_required
def item_update_page(game_id, item_id):
    if request.method == "POST":
        try:
            file_picture = request.files["picture"]
            uploaded_picture = images.save(file_picture)
            form_name = request.form["name"]
            form_item_type = request.form["item_type"]
            form_rarity = request.form["rarity"]
            form_price = request.form["price"]
            item = Item(item_id, game_id, uploaded_picture, form_name, form_item_type, form_rarity, form_price)
            db.update_item(item)
            return render_template("item_update_result.html", game_id=game_id)
        except Exception:
            return redirect(url_for("item_update_page", game_id=game_id, item_id=item_id))
    return render_template("item_update.html")


@app.route("/store/<int:game_id>/<int:item_id>/item_purchase")
@login_required
def item_purchase_page(game_id, item_id):
    game = db.get_game(game_id)
    item = db.get_item(game_id, item_id)
    return render_template("item_purchase.html", game=game, item=item)


@app.route("/store/<int:game_id>/<int:item_id>/item_purchase_result")
@login_required
def item_purchase_result_page(game_id, item_id):
    item = db.get_item(game_id, item_id)
    if current_user.is_admin or current_user.balance >= item.price:
        already_has_item = db.add_item_to_user(item.item_id, game_id, current_user.id)
        db.decrease_balance_of_user(current_user.id, item.price)
        db.set_num_of_shared_items_for_all_friends(current_user.id)
    return render_template("item_purchase_result.html", item=item, already_has_item=already_has_item)


@app.route("/store/<int:item_id>/item_edit", methods=['GET', 'POST'])
@login_required
def item_edit_page(item_id):
    if request.method == "POST":
        form_color = request.form["color"]
        form_is_favorite = request.form["is_favorite"]
        form_is_equipped = request.form["is_equipped"]
        db.edit_item(item_id, form_color, form_is_favorite, form_is_equipped)
        return redirect(url_for("item_edit_result_page"))
    return render_template("item_edit.html")


@app.route("/store/item_edit_result")
@login_required
def item_edit_result_page():
    return render_template("item_edit_result.html")


# Screenshot Comments
@app.route("/store/<int:game_id>/<int:screenshot_id>/comments", methods=['GET', 'POST'])
def screenshot_comments_page(game_id, screenshot_id):
    if request.method == "POST":
        comment_id_to_delete = request.form.get("delete-button")
        is_getting_deleted = comment_id_to_delete is not None
        if is_getting_deleted:
            db.delete_screenshot_comment(comment_id_to_delete)
        else:
            form_content = request.form["content"]
            form_reaction = request.form["reaction"]
            form_font_size = request.form["font_size"]
            form_color = request.form["color"]
            db.add_screenshot_comment(current_user.id, game_id, screenshot_id,
                                      form_content, form_reaction, form_font_size, form_color)
        return redirect(url_for("screenshot_comments_page", game_id=game_id, screenshot_id=screenshot_id))

    screenshot_comments = db.get_screenshot_comments(game_id, screenshot_id)
    return render_template("screenshot_comments.html", game_id=game_id, screenshot_id=screenshot_id,
                           screenshot_comments=screenshot_comments)


@app.route("/game_add_result")
@login_required
def game_add_page_result_page():
    if not current_user.is_admin:
        return render_template('not_allowed.html')
    return render_template("game_add_result.html")


@app.route("/store/<int:game_id>/game_rate", methods=['GET', 'POST'])
@login_required
def game_rate_page(game_id):
    if request.method == "POST":
        form_rating = request.form["rating"]
        already_rated = db.is_already_rated(current_user.id, game_id)
        db.update_rating_of_game(game_id, current_user.id, form_rating, already_rated)
        return render_template("game_rate_result.html", rated_before=already_rated)
    return render_template("game_rate.html")


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
            db.set_num_of_shared_games_for_all_friends(current_user.id)
    return render_template("game_purchase_result.html", game=game, success=success)


@app.route("/profile/code_enter", methods=['GET', 'POST'])
@login_required
def code_enter_page():
    if request.method == "POST":
        form_code = request.form["code"]
        valid = db.check_code(form_code)
        if valid:
            db.add_balance_to_user(current_user.id)
        return render_template("code_enter_result.html", valid=valid)
    return render_template("code_enter.html")

# -----------------------------------------------------------------------


@app.route("/profile/process_friend_request_response", methods=['POST'])
@login_required
def process_friend_request_response():
    user_id_from = request.form.get("user_id_from")
    user_id_to = request.form.get("user_id_to")
    user_name_from = db.get_user(user_id_from).user_name

    if request.form.get("response") == "accepted":
        db.add_friend(user_id_to, user_id_from)
        db.set_num_of_shared_games(user_id_to, user_id_from)
        db.set_num_of_shared_items(user_id_to, user_id_from)
        return jsonify({"fillerText": user_name_from + " has been added to your friends!"})
    elif request.form.get("response") == "declined":
        db.remove_request(user_id_from, user_id_to)
        return jsonify({"fillerText": "You declined " + user_name_from + "'s friend request."})
    else:
        db.remove_request(user_id_from, user_id_to)
        return jsonify({"fillerText": "You cancelled the request."})


@app.route("/profile/friend_add", methods=['GET', 'POST'])
@login_required
def friend_add_page():
    if request.method == "POST":
        form_user_name = request.form["user_name"]
        user_id_to = db.get_user_id(form_user_name)
        is_valid = user_id_to is not None
        are_friends = False
        is_self = False
        already_sent = False
        user_to = None

        if is_valid:
            user_to = db.get_user(user_id_to)
            are_friends = db.check_if_already_friends(current_user.id, user_id_to)
            if current_user.id == user_id_to:
                is_self = True
            already_sent = db.check_friend_request(current_user.id, user_id_to)
            if not are_friends and not is_self and not already_sent:
                db.send_friend_request(current_user.id, user_id_to)

        return render_template("friend_add_result.html", valid=is_valid, are_friends=are_friends, is_self=is_self,
                               already_sent=already_sent, user_to=user_to)
    return render_template("friend_add.html")


@app.route("/profile/process_game_favouriting", methods=['POST'])
@login_required
def process_game_favouriting():
    operation = request.form.get("operation")
    user_id = request.form.get("user_id")
    game_id = request.form.get("game_id")

    if operation == "ADD":
        db.update_game_favourite_variable(user_id, game_id, "ADD")
        return jsonify({"responseText": "Added to favourites"}, {"column_favourite": "*FAVOURITE*"})
    else:
        db.update_game_favourite_variable(user_id, game_id, "REMOVE")
        return jsonify({"responseText": "Removed from favourites"}, {"column_favourite": ""})


@app.route("/profile/process_play_game", methods=['POST'])
@login_required
def process_play_game():
    user_id = request.form.get("user_id")
    game_id = request.form.get("game_id")
    time_played = request.form.get("time_played")

    db.increment_time_played(user_id, game_id)

    return jsonify({"time_played": str(int(time_played) + 1)})


@app.route("/profile/process_friend_operations", methods=['POST'])
@login_required
def process_friend_operations():
    operation = request.form.get("operation")
    user1_id = request.form.get("user1_id")
    user2_id = request.form.get("user2_id")

    response = db.update_friend_variable(user1_id, user2_id, operation)

    return jsonify({"responseText": response})

if __name__ == "__main__":
    app.run()
