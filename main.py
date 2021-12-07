import datetime
import os
import time as t
from datetime import date, timedelta
import random as r

from dotenv import dotenv_values
from flask import Flask, render_template, redirect, url_for, flash, request, abort
from flask_bootstrap import Bootstrap
from flask_ckeditor import CKEditor
from flask_gravatar import Gravatar
from flask_login import (UserMixin, login_user, LoginManager, login_required, current_user, logout_user,
                         fresh_login_required)
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

from functions import create_folder_struct, add_music
from email_class import SendEmail
from forms import (CreatePostForm, RegisterForm, LoginForm, CommentForm, ContactForm, EmailPassword, CodeConfirmation,
                   ResetPassword, ProfileContent, SongUpload)

UPLOAD_FOLDER = "static/uploads/users"
ALLOWED_EXTENSIONS = {"jpg", "png"}
app = Flask(__name__)
config = dotenv_values(".env")
SECRET_KEY = os.urandom(32)  # This is for testing
app.config['SECRET_KEY'] = SECRET_KEY  # This is for testing
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["ALLOWED_EXTENSIONS"] = ALLOWED_EXTENSIONS
app.config["MAX_CONTENT_LENGTH"] = 1000 * 1024 * 1024 # 1000mb
ckeditor = CKEditor(app)
Bootstrap(app)
send_email = SendEmail()

# Gravatar Init
gravatar = Gravatar(app,
                    size=100,
                    rating='g',
                    default='retro',
                    force_default=False,
                    force_lower=False,
                    use_ssl=False,
                    base_url=None)

# #CONNECT TO DB
# app.config['SQLALCHEMY_DATABASE_URL'] = os.environ.get("DATABASE_URL", "sqlite:///blog.db")
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///blog.db"  # This is for testing
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['REMEMBER_COOKIE_DURATION'] = timedelta(seconds=3600)
app.config["FORCE_HOST_FOR_REDIRECTS"] = None
app.add_url_rule("/", endpoint="get_all_posts")
app.add_url_rule("/new-post", endpoint="add_new_post")
app.add_url_rule(rule="/edit-post/<int:post_id>", endpoint="edit_post")
app.add_url_rule(rule="/delete/<int:post_id>", endpoint="delete_post")
db = SQLAlchemy(app)

# #USER LOGIN
login_manager = LoginManager()
login_manager.session_protection = "strong"
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# #CONFIGURE TABLES

class BlogPost(db.Model):
    __tablename__ = "blog_posts"
    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    author = relationship("User", back_populates="posts")
    title = db.Column(db.String(250), unique=True, nullable=False)
    subtitle = db.Column(db.String(250), nullable=False)
    date = db.Column(db.String(250), nullable=False)
    body = db.Column(db.Text, nullable=False)
    img_url = db.Column(db.String(250), nullable=False)


class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    account_type = db.Column(db.String(255), nullable=False)
    creation_date = db.Column(db.String(250), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    name = db.Column(db.String(255), nullable=False)
    password = db.Column(db.String(255), nullable=False)
    posts = relationship("BlogPost", back_populates="author")
    comments = relationship("Comment", back_populates="author")
    profile = relationship("Profile", back_populates="user")
    songs = relationship("Song", back_populates="user")


class Profile(db.Model):
    __tablename__ = "user_profiles"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    user = relationship("User", back_populates="profile")
    profile_picture = db.Column(db.String(255), nullable=True)
    profile_bio = db.Column(db.String(255))


class Song(db.Model):
    __tablename__ = "songs"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    user = relationship("User", back_populates="songs")
    artist = db.Column(db.String(255), nullable=True)
    album = db.Column(db.String(255), nullable=True)
    album_art = db.Column(db.String(255), nullable=True)
    song_file = db.Column(db.String(255), nullable=True)
    song_name = db.Column(db.String(255), nullable=True)


class Comment(db.Model):
    __tablename__ = "comments"
    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    post_id = db.Column(db.Integer, nullable=False)
    author = relationship("User", back_populates="comments")
    comment = db.Column(db.String(255), nullable=False)
    date = db.Column(db.String(255), nullable=False)
    time = db.Column(db.String(255), nullable=False)


db.create_all()  # This is for database creation


@app.route('/')
@app.endpoint("/")
def get_all_posts():
    title = "Andrew's Blog"
    year = datetime.datetime.now().year
    if current_user.is_authenticated:
        user = User.query.get(current_user.id)

        # print(user.account_type)
    else:
        user = None
    posts = BlogPost.query.all()
    return render_template("index.html",
                           all_posts=posts,
                           is_authenticated=current_user.is_authenticated,
                           user=user,
                           year=year,
                           title=title
                           )


@app.route('/register', methods=["POST", "GET"])
def register():
    title = "Register | Andrew's Blog"
    user = current_user
    form = RegisterForm()
    if form.validate_on_submit():
        if User.query.filter_by(email=form.email.data).first():
            flash("You've already signed up with that email, log in instead!")
            return redirect(url_for("login"))
        else:
            create_folder_struct(request.form.get("name"))
            salted_password = generate_password_hash(
                password=request.form.get("password"),
                method="pbkdf2:sha256",
                salt_length=8)
            new_user = User(
                email=request.form.get("email"),
                account_type=request.form.get("account_type"),
                creation_date=datetime.date.today(),
                name=request.form.get("name"),
                password=salted_password
            )
            db.session.add(new_user)
            db.session.commit()

            user = User.query.filter_by(email=form.email.data).first()
            user_profile = Profile(
                user=user,
                profile_picture=url_for("static", filename="img/blank-pro-pic.png"),
                profile_bio=""
            )
            db.session.add(user_profile)
            db.session.commit()

            login_user(new_user)

            return redirect(url_for("get_all_posts"))

    return render_template("register.html", form=form, user=user, title=title)


@app.route('/login', methods=["POST", "GET"])
def login():
    title = "Login | Andrew's Blog"
    user = current_user
    form = LoginForm()
    if request.method == "POST":
        _redirect = False
        if request.args.get("next"):
            next_url = request.args.get("next")
            if request.args.get("next") == "edit_post" or request.args.get("next") == "delete_post":
                post_id = request.args.get("post_id")
                _redirect = True
            else:
                _redirect = False
        else:
            next_url = "get_all_posts"
        email = request.form.get("email")
        password = request.form.get("password")
        user = User.query.filter_by(email=email).first()
        if check_password_hash(user.password, password):
            remember_me = request.form.get("remember_me")
            if remember_me:
                login_user(user, remember=True)
            else:
                login_user(user)
            if _redirect:
                return redirect(url_for(next_url, post_id=post_id))
            else:
                return redirect(url_for(next_url))
        else:
            flash("Your username or password is incorrect", category="Unsuccessful_Login")
            return redirect(url_for("login"))
    return render_template("login.html", form=form, user=user, title=title)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('get_all_posts'))


@app.route('/profile/<int:_id>', methods=["POST", "GET"])
def profile(_id):
    if current_user.is_authenticated:
        user_data = User.query.get(current_user.id)
    else:
        user_data = {
            "id": 0
        }
    profile_data = User.query.get(_id)
    title = f"{profile_data.name} | Andrew's Blog"
    user = current_user
    return render_template(
        "profile.html",
        is_authenticated=user.is_authenticated,
        user=user_data,
        title=title,
        profile_data=profile_data,
    )


@app.route('/profile/<int:_id>/edit-profile', methods=["POST", "GET"])
@login_required
@fresh_login_required
def edit_profile(_id):
    user_data = User.query.get(_id)
    title = f"Edit Profile | Andrew's Blog"
    user = current_user
    form = ProfileContent()
    if form.validate_on_submit():
        pic_dir = f"/static/uploads/users/{user_data.name.replace(' ', '_').lower()}/data/profile-picture"
        root_path = "./static/uploads/users"
        user_path = f"{user_data.name.replace(' ', '_').lower()}/data/profile-picture"
        new_picture = form.profile_picture.data
        filename = new_picture.filename
        user_profile = Profile.query.get(_id)
        if not new_picture.filename:
            user_profile.profile_picture = user_profile.profile_picture
        else:
            user_profile.profile_picture = f"{pic_dir}/{filename}"
            new_picture.save(os.path.join(root_path, user_path, filename))
        if form.profile_bio.data == "":
            user_profile.profile_bio = user_profile.profile_bio
        else:
            user_profile.profile_bio = form.profile_bio.data
        db.session.commit()
        return redirect(url_for("profile", _id=_id))
    if current_user.id == user_data.id:
        return render_template("edit-profile.html",
                               is_authenticated=user.is_authenticated,
                               title=title,
                               user=user_data,
                               form=form
                               )
    else:
        return abort(401, response="aborts/forbidden.html")


@app.route("/post/<int:post_id>", methods=["POST", "GET"])
def show_post(post_id):
    user = current_user
    requested_post = BlogPost.query.get(post_id)
    title = f"{requested_post.title} | {requested_post.subtitle} | Andrew's Blog"
    comments = Comment.query.all()
    form = CommentForm()
    struct_time = t.localtime(t.time())
    time_now = t.strftime("%I:%M %p", struct_time)
    if form.validate_on_submit():
        if not user.is_authenticated:
            flash("You need to log in or register to comment.")
            return redirect(url_for("login"))
        else:
            new_comment = Comment(
                post_id=post_id,
                author=current_user,
                comment=form.comment.data,
                date=date.today().strftime("%B %d, %Y"),
                time=time_now
            )
            db.session.add(new_comment)
            db.session.commit()
            return redirect(url_for("show_post", post_id=requested_post.id))
    form.comment.data = ""
    return render_template(
        "post.html",
        post=requested_post,
        is_authenticated=user.is_authenticated,
        user=user,
        comments=comments,
        form=form,
        title=title
    )


@app.route("/about")
def about():
    title = "About | Andrew's Blog"
    user = current_user
    return render_template("about.html", is_authenticated=user.is_authenticated, user=user, title=title)


@app.route("/contact", methods=["POST", "GET"])
def contact():
    title = "Contact | Andrew's Blog"
    form = ContactForm()
    user = current_user

    if user.is_authenticated:
        form.name.data = user.name
        form.email.data = user.email

    if form.validate_on_submit():
        msg_info = {
            "name": form.name.data,
            "email": form.email.data,
            "phone": form.phone.data,
            "msg": form.message.data
        }
        send_email.send_email_message(msg_info)
        flash(message="Your message was sent, successfully!", category="Email Sent Success")
        return redirect(url_for("contact"))
    return render_template("contact.html", is_authenticated=user.is_authenticated, user=user, form=form, title=title)


@app.route("/new-post", methods=["POST", "GET"])
@app.endpoint("/new-post")
@login_required
@fresh_login_required
def add_new_post():
    title = "New Post | Andrew's Blog"
    user = current_user
    form = CreatePostForm()
    if user.account_type != "Admin":
        # abort(401, description="Unauthorized access")
        return abort(401, response="aborts/forbidden.html")
    else:
        if form.validate_on_submit():
            new_post = BlogPost(
                title=form.title.data,
                subtitle=form.subtitle.data,
                body=form.body.data,
                author=current_user,
                img_url=form.img_url.data,
                date=date.today().strftime("%B %d, %Y")
            )
            db.session.add(new_post)
            db.session.commit()
            return redirect(url_for("get_all_posts"))
        return render_template("make-post.html",
                               form=form,
                               is_authenticated=user.is_authenticated,
                               user=user,
                               title=title
                               )


@app.route("/edit-post/<int:post_id>", methods=["POST", "GET"])
@app.endpoint("edit_post")
@login_required
@fresh_login_required
def edit_post(post_id):
    user = current_user
    post = BlogPost.query.get(post_id)
    title = f"Edit {post.title} | {post.subtitle} | Andrew's Blog"
    if post.author_id == user.id:
        edit_form = CreatePostForm(
            title=post.title,
            subtitle=post.subtitle,
            img_url=post.img_url,
            body=post.body
        )
        if request.method == "POST":
            if edit_form.validate_on_submit():
                post.title = edit_form.title.data
                post.subtitle = edit_form.subtitle.data
                post.img_url = edit_form.img_url.data
                post.body = edit_form.body.data
                db.session.commit()
                return redirect(url_for("show_post", post_id=post.id))
            else:
                print("Didn't work")
        # else:
        #     print("Get, not POST")

        return render_template(
            "make-post.html",
            form=edit_form,
            is_authenticated=user.is_authenticated,
            is_edit=True,
            user=user,
            title=title
        )
    else:
        # print(f"User ID: {user.id}\nAuthor ID: {post.author_id}")
        return abort(401, response="aborts/forbidden.html")


@app.route("/delete/<int:post_id>")
@app.endpoint("delete_post")
@login_required
@fresh_login_required
def delete_post(post_id):
    post_to_delete = BlogPost.query.get(post_id)
    db.session.delete(post_to_delete)
    db.session.commit()
    return redirect(url_for('get_all_posts'))


@app.route("/reset-password?<string:step>&<string:arg>", methods=["POST", "GET"])
def forgot_password(step, arg):
    if step == "Password Reset":
        form = ResetPassword()
        form.step.data = step
    elif step == "Code Confirmation":
        user = User.query.filter_by(email=arg).first()
        user_data = {
            "name": user.name,
            "email": user.email
        }
        conf_code = r.randint(100000, 600000)
        send_email.send_reset_conf(user_data, conf_code)
        form = CodeConfirmation()
        form.code.data = conf_code
        form.step.data = step
    else:
        form = EmailPassword()
        form.step.data = step
    if request.method == "POST":
        if form.validate_on_submit():
            if request.form.get("step") == "Email Confirmation":
                user_email = request.form.get("email")
                req_user = User.query.filter_by(email=user_email).first()
                if req_user:
                    flash(f"A confirmation code was sent to email: {req_user.email}")
                    return redirect(url_for("forgot_password", step="Code Confirmation", arg=req_user.email))
            elif request.form.get("step") == "Code Confirmation":
                user_email = arg
                code = request.form.get("code")
                sub_code = request.form.get("code_conf")
                if code == sub_code:
                    return redirect(url_for("forgot_password", step="Password Reset", arg=user_email))
            elif request.form.get("step") == "Password Reset":
                salted_password = generate_password_hash(
                    password=request.form.get("password"),
                    method="pbkdf2:sha256",
                    salt_length=8
                )
                req_user = User.query.filter_by(email=arg).first()
                req_user.password = salted_password
                db.session.commit()
                return redirect(url_for("login"))

    return render_template("forgot.html", form=form)


@app.route("/music-player", methods=["POST", "GET"])
def music_player():
    all_songs = Song.query.all()
    return render_template("music-player.html", songs=all_songs)


@app.route("/song-upload", methods=["POST", "GET"])
@login_required
def song_upload():
    user = User.query.get(current_user.id)
    form = SongUpload()
    is_authenticated = current_user.is_authenticated
    title = "Upload a new song | Andrew's Blog"
    if request.method == "POST":
        if form.validate_on_submit():
            form_data = {
                "artist": form.artist.data,
                "album": form.album.data,
                "album_art": form.album_art.data,
                "song": form.song.data
            }
            add_song = add_music(user, form_data)
            root_path = f"static/uploads/users/{user.name.replace(' ', '_').lower()}/data/music"
            artist_dir = f"{root_path}/{form_data['artist'].replace(' ', '_')}"
            album_dir = f"{artist_dir}/{form_data['album'].replace(' ', '_')}"
            album_art_filename = form_data["album_art"].filename
            song_filename = form_data["song"].filename
            if add_song:
                form_data["album_art"].save(os.path.join(album_dir, album_art_filename))
                form_data["song"].save(os.path.join(album_dir, song_filename))
                song = f"{form.song.data.filename}"
                song = song.replace(" ", "_")
                album_art = f"{form.album_art.data.filename}"
                album_art = album_art.replace(" ", "_")
                os.replace(f"{album_dir}/{song_filename}", f"{album_dir}/{song}")
                os.replace(f"{album_dir}/{album_art_filename}", f"{album_dir}/{album_art}")
                new_song = Song(
                    user=user,
                    artist=form_data["artist"],
                    album=form_data["album"],
                    album_art=f"{album_dir}/{album_art}",
                    song_file=f"{album_dir}/{song}",
                    song_name=song_filename[:-4]
                )
                db.session.add(new_song)
                db.session.commit()
                return redirect(url_for("profile", _id=user.id))
            else:
                flash("Song either already exists or there was an issue uploading the files\nPlease try again")
                return redirect(url_for("song_upload"))
    return render_template("song-upload.html", form=form, is_authenticated=is_authenticated, title=title, user=user)


# Fresh Login Function
@login_manager.needs_refresh_handler
def refresh():
    flash("Re-authentication required")
    if request.endpoint == "edit_post" or request.endpoint == "delete_post":
        return redirect(url_for("login", next=request.endpoint, post_id=request.url[-1]))
    else:
        return redirect(url_for("login", next=request.endpoint))


# Error Handling Functions
@app.errorhandler(401)
def forbidden(e):
    if current_user.is_authenticated:
        user = User.query.get(current_user.id)
    else:
        user = None
    return render_template(
        "/aborts/forbidden.html",
        error=e,
        is_authenticated=current_user.is_authenticated,
        user=user
    ), 401


@app.errorhandler(404)
def not_found(e):
    if current_user.is_authenticated:
        user = User.query.get(current_user.id)
    else:
        user = None
    return render_template(
        "/aborts/not-found.html",
        error=e,
        is_authenticated=current_user.is_authenticated,
        user=user
    ), 404


if __name__ == "__main__":
    app.run(host='localhost', port=5000, debug=True)
