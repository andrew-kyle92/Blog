import datetime
import json
import os
import random as r
import secrets
import time as t
from datetime import date, timedelta

import flask
from dotenv import dotenv_values
from flask import Flask, render_template, redirect, url_for, flash, request, abort, session
from flask_bootstrap import Bootstrap
from flask_ckeditor import CKEditor
from flask_gravatar import Gravatar
from flask_login import (UserMixin, login_user, LoginManager, login_required, current_user, logout_user,
                         fresh_login_required)
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from werkzeug.datastructures import CombinedMultiDict
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

from apis import APIs
from email_class import SendEmail
from forms import (CreatePostForm, RegisterForm, LoginForm, CommentForm, ContactForm, EmailPassword, CodeConfirmation,
                   ResetPassword, ProfileContent, SongUpload, EditSettings, ChangePassword, EditUser, TabUpload)
from functions import create_folder_struct, add_music, update_account, AttributeDict
from sql_queries import (get_user_songs, delete_song, get_all_artists_tabs, upload_tab, get_all_song_tabs, get_song,
                         query_users, get_all_songs_audio, get_all_artists_audio, get_song_audio, get_all_albums_audio,
                         get_album_songs)

UPLOAD_FOLDER = "static/uploads"
ALLOWED_EXTENSIONS = {"jpg", "png", "gp3", "gp4", "gp5", "gpx", "gp"}
app = Flask(__name__)
config = dotenv_values(".env")
app.config['SECRET_KEY'] = config.get("SECRET_KEY")
app.config["PERMANENT_SESSION_LIFETIME"] = datetime.timedelta(minutes=20)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["ALLOWED_EXTENSIONS"] = ALLOWED_EXTENSIONS
app.config["MAX_CONTENT_LENGTH"] = 1000 * 1024 * 1024  # 1000mb
app.config['FLASK_ADMIN_SWATCH'] = 'cerulean'
ckeditor = CKEditor(app)
Bootstrap(app)
send_email = SendEmail()
apis = APIs()

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
app.config['SQLALCHEMY_DATABASE_URI'] = config.get("DATABASE_URL", "postgresql:///blog.db")
# app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql:///blogdb"  # This is for testing
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['REMEMBER_COOKIE_DURATION'] = timedelta(seconds=3600)
app.config["FORCE_HOST_FOR_REDIRECTS"] = None
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.add_url_rule("/", endpoint="get_all_posts")
app.add_url_rule("/new-post", endpoint="add_new_post")
app.add_url_rule(rule="/edit-post", endpoint="edit_post")
app.add_url_rule(rule="/delete", endpoint="delete_post")
app.add_url_rule("/profile/settings", endpoint="settings")
app.add_url_rule(rule="/profile/settings/edit", endpoint="settings_edit")
app.add_url_rule(rule="/profile/edit-profile", endpoint="edit_profile")
db = SQLAlchemy(app)

# #USER LOGIN
login_manager = LoginManager()
login_manager.session_protection = "basic"
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
    verification_code = db.Column(db.String(6))
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


class Artist(db.Model):
    __tablename__ = "artists"
    id = db.Column(db.Integer, primary_key=True)
    artist = db.Column(db.String(255), nullable=False)
    albums = relationship("Album", back_populates="artist")
    songs = relationship("Song", back_populates="artist")


class Album(db.Model):
    __tablename__ = "albums"
    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey("artists.id"))
    artist = relationship("Artist", back_populates="albums")
    album = db.Column(db.String(255), nullable=False)
    songs = relationship("Song", back_populates="album")


class Song(db.Model):
    __tablename__ = "songs"
    id = db.Column(db.Integer, primary_key=True)
    ref_id = db.Column(db.String(255), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    user = relationship("User", back_populates="songs")
    artist_id = db.Column(db.Integer, db.ForeignKey("artists.id"))
    artist = relationship("Artist", back_populates="songs")
    album_id = db.Column(db.Integer, db.ForeignKey("albums.id"))
    album = relationship("Album", back_populates="songs")
    album_art = db.Column(db.String(255), nullable=True)
    song_file = db.Column(db.String(255), nullable=True)
    song_name = db.Column(db.String(255), nullable=True)
    track_number = db.Column(db.Integer, nullable=True)


class Comment(db.Model):
    __tablename__ = "comments"
    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    post_id = db.Column(db.Integer, nullable=False)
    author = relationship("User", back_populates="comments")
    comment = db.Column(db.String(255), nullable=False)
    date = db.Column(db.String(255), nullable=False)
    time = db.Column(db.String(255), nullable=False)


db.create_all()  # This is for database creation for test environment


@app.route('/')
@app.endpoint("/")
def get_all_posts():
    title = "Andrew's Blog"
    year = datetime.datetime.now().year
    api_articles = json.dumps(session["articles"]) if "articles" in session.keys() else None
    if current_user.is_authenticated:
        user = User.query.get(current_user.id)
    else:
        user = None
    posts = BlogPost.query.all()
    scripts = ["js/newsAPI.js"]
    return render_template("routes/main-site/index.html",
                           all_posts=posts,
                           api_articles=api_articles,
                           is_authenticated=current_user.is_authenticated,
                           user=user,
                           year=year,
                           title=title,
                           scripts=scripts
                           )


@app.route('/register', methods=["POST", "GET"])
def register():
    title = "Register | Andrew's Blog"
    user = current_user
    year = datetime.datetime.now().year
    form = RegisterForm(request.form, meta={"csrf_context": flask.session})
    if request.method == "POST" and form.validate():
        if User.query.filter_by(email=form.email.data).first():
            flash("You've already signed up with that email, log in instead!")
            return redirect(url_for("login"))
        else:
            salted_password = generate_password_hash(
                password=request.form.get("password"),
                method="pbkdf2:sha256",
                salt_length=8)
            new_user = User(
                email=request.form.get("email"),
                account_type=request.form.get("account_type"),
                creation_date=datetime.date.today(),
                name=request.form.get("name"),
                password=salted_password,
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

            create_folder_struct(user)

            login_user(new_user)

            return redirect(url_for("get_all_posts"))

    return render_template("routes/main-site/register.html", form=form, user=user, title=title, year=year)


@app.route('/login', methods=["POST", "GET"])
def login():
    title = "Login | Andrew's Blog"
    user = current_user
    form = LoginForm(request.form, meta={"csrf_context": flask.session})
    year = datetime.datetime.now().year
    if request.method == "POST" and form.validate():
        _redirect = False
        post_id_needed = False
        user_id_needed = False
        if request.args.get("next"):
            next_url = request.args.get("next")
            if request.args.get("next") == "edit_post" or request.args.get("next") == "delete_post":
                post_id = request.args.get("post_id")
                post_id_needed = True
                _redirect = True
            elif request.args.get("next") == "settings" or request.args.get("next") == "edit-settings" or \
                    request.args.get("next") == "user_edit":
                user_id = request.args.get("user_id")
                user_id_needed = True
                _redirect = True
            else:
                _redirect = False
        else:
            next_url = "get_all_posts"
        email = request.form.get("email")
        password = request.form.get("password")
        user = User.query.filter_by(email=email.lower()).first()
        if user is None:
            flash(f"There is no user with email: {email}. Make sure there are no typos and try again",
                  category="non_member"
                  )
            return redirect(url_for("login"))
        else:
            if check_password_hash(user.password, password):
                remember_me = request.form.get("remember_me")
                if remember_me:
                    login_user(user, remember=True)
                else:
                    login_user(user)
                if _redirect and post_id_needed:
                    return redirect(url_for(next_url, post_id=post_id))
                elif _redirect and user_id_needed:
                    return redirect(url_for(next_url, user_id=user_id))
                else:
                    return redirect(url_for(next_url))
            else:
                flash("Your username or password are incorrect", category="unsuccessful_login")
                return redirect(url_for("login"))
    return render_template("routes/main-site/login.html", form=form, user=user, title=title, year=year)


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
    year = datetime.datetime.now().year
    return render_template(
        "routes/main-site/profile.html",
        is_authenticated=user.is_authenticated,
        user=user_data,
        title=title,
        profile_data=profile_data,
        year=year
    )


@app.route('/profile/edit-profile', methods=["POST", "GET"])
@app.endpoint("edit_profile")
@login_required
@fresh_login_required
def edit_profile():
    _id = request.args.get("_id")
    print(request.args)
    user_data = User.query.get(_id)
    title = f"Edit Profile | Andrew's Blog"
    user = current_user
    year = datetime.datetime.now().year
    form = ProfileContent(CombinedMultiDict((request.files, request.form)), meta={"csrf_context": flask.session})
    if request.method == "POST" and form.validate():
        pic_dir = f"/static/uploads/users/" \
                  f"{user_data.id}-{user_data.name.replace(' ', '_').lower()}/data/profile-picture"
        root_path = "./static/uploads/users"
        user_path = f"{user_data.id}-{user_data.name.replace(' ', '_').lower()}/data/profile-picture"
        new_picture = form.profile_picture.data
        filename = new_picture.filename
        user_profile = Profile.query.get(_id)
        if not new_picture.filename:
            user_profile.profile_picture = user_profile.profile_picture
        else:
            user_profile.profile_picture = f"{pic_dir}/{filename}"
            request.files['profile_picture'].save(os.path.join(root_path, user_path, filename))
        if form.profile_bio.data == "":
            user_profile.profile_bio = user_profile.profile_bio
        else:
            user_profile.profile_bio = form.profile_bio.data
        db.session.commit()
        return redirect(url_for("profile", _id=_id))
    if current_user.id == user_data.id:
        return render_template("routes/main-site/edit-profile.html",
                               is_authenticated=user.is_authenticated,
                               title=title,
                               user=user_data,
                               form=form,
                               year=year
                               )
    else:
        return abort(401, response="aborts/forbidden.html")


@app.route("/post", methods=["POST", "GET"])
def show_post():
    requested_post = None
    post_id = request.args.get("post_id")
    api_post = request.args.get("API")
    publishedDate = request.args.get("publishDate")
    articles = session["articles"] if "articles" in session.keys() else None
    if articles is not None:
        print(len(articles))
    user = current_user
    if not api_post:
        requested_post = BlogPost.query.get(post_id)
    else:
        for article in articles:
            if article["author"] is not None and article["publishedAt"] == publishedDate:
                articleDict = AttributeDict(article)
                requested_post = articleDict
                break
            elif article["author"] is None:
                if article["publishedAt"] == publishedDate:
                    articleDict = AttributeDict(article)
                    requested_post = articleDict
                    break
    title = f"{requested_post.title} | Andrew's Blog"
    comments = Comment.query.all()
    year = datetime.datetime.now().year
    form = CommentForm(request.form, meta={"csrf_context": flask.session})
    struct_time = t.localtime(t.time())
    time_now = t.strftime("%I:%M %p", struct_time)
    if request.method == "POST" and form.validate():
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
        "routes/main-site/post.html",
        post=requested_post,
        is_authenticated=user.is_authenticated,
        user=user,
        comments=comments,
        form=form,
        title=title,
        year=year,
        api=api_post
    )


@app.route("/about")
def about():
    title = "About | Andrew's Blog"
    user = current_user
    year = datetime.datetime.now().year
    return render_template("routes/main-site/about.html", is_authenticated=user.is_authenticated, user=user, title=title, year=year)


@app.route("/contact", methods=["POST", "GET"])
def contact():
    title = "Contact | Andrew's Blog"
    form = ContactForm(request.form, meta={"csrf_context": flask.session})
    user = current_user
    year = datetime.datetime.now().year

    if user.is_authenticated:
        form.name.data = user.name
        form.email.data = user.email

    if request.method == "POST" and form.validate():
        msg_info = {
            "name": form.name.data,
            "email": form.email.data,
            "phone": form.phone.data,
            "msg": form.message.data
        }
        send_email.send_email_message(msg_info)
        flash(message="Your message was sent, successfully!", category="Email Sent Success")
        return redirect(url_for("contact"))
    return render_template("routes/main-site/contact.html",
                           is_authenticated=user.is_authenticated,
                           user=user,
                           form=form,
                           title=title,
                           year=year
                           )


@app.route("/new-post", methods=["POST", "GET"])
@login_required
@fresh_login_required
def add_new_post():
    title = "New Post | Andrew's Blog"
    user = User.query.get(current_user.id)
    year = datetime.datetime.now().year
    form = CreatePostForm(request.form, meta={"csrf_context": flask.session})
    if user.account_type == "Admin" or user.account_type == "Super-Admin":
        if request.method == "POST" and form.validate():
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
        return render_template("routes/main-site/make-post.html",
                               form=form,
                               is_authenticated=current_user.is_authenticated,
                               user=user,
                               title=title,
                               year=year
                               )

    else:
        # abort(401, description="Unauthorized access")
        return abort(401, response="aborts/forbidden.html")


@app.route("/edit-post", methods=["POST", "GET"])
@app.endpoint("edit_post")
@login_required
@fresh_login_required
def edit_post():
    post_id = request.args.get("post_id")
    user = current_user
    post = BlogPost.query.get(post_id)
    year = datetime.datetime.now().year
    title = f"Edit {post.title} | {post.subtitle} | Andrew's Blog"
    if post.author_id == user.id:
        form = CreatePostForm(request.form, meta={"csrf_context": flask.session})
        if request.method == "POST" and form.validate():
            post.title = form.title.data
            post.subtitle = form.subtitle.data
            post.img_url = form.img_url.data
            post.body = form.body.data
            db.session.commit()
            return redirect(url_for("show_post", post_id=post.id))
        else:
            form.title.data = post.title
            form.subtitle.data = post.subtitle
            form.img_url.data = post.img_url
            form.body.data = post.body
            return render_template(
                "routes/main-site/make-post.html",
                form=form,
                is_authenticated=user.is_authenticated,
                is_edit=True,
                user=user,
                title=title,
                year=year
            )
    else:
        # print(f"User ID: {user.id}\nAuthor ID: {post.author_id}")
        return abort(401, response="aborts/forbidden.html")


@app.route("/delete", methods=["POST", "GET"])
@login_required
@fresh_login_required
def delete_post():
    post_id = request.args.get("post_id")
    post_to_delete = BlogPost.query.get(post_id)
    db.session.delete(post_to_delete)
    db.session.commit()
    return redirect(url_for('get_all_posts'))


@app.route("/reset-password", methods=["POST", "GET"])
def forgot_password():
    year = datetime.datetime.now().year
    step = request.args.get("step")
    user = request.args.get("user")
    if step == "Password Reset":
        form = ResetPassword(request.form, meta={"csrf_context": flask.session})
        form.step.data = step
    elif step == "Code Confirmation":
        form = CodeConfirmation(request.form, meta={"csrf_context": flask.session})
        form.step.data = step
    else:
        form = EmailPassword(request.form, meta={"csrf_context": flask.session})
        form.step.data = step
    if request.method == "POST":
        if form.validate():
            if step == "Email Confirmation":
                user_email = request.form.get("email")
                req_user = User.query.filter_by(email=user_email).first()
                user_data = {
                    "name": req_user.name,
                    "email": req_user.email
                }
                if req_user:
                    conf_code = r.randint(100000, 600000)
                    req_user.verification_code = conf_code
                    db.session.commit()
                    send_email.send_reset_conf(user_data, conf_code)
                    flash(f"A confirmation code was sent to email: {req_user.email}")
                    return redirect(url_for("forgot_password",
                                            step="Code Confirmation", user=req_user.email))
            elif step == "Code Confirmation":
                user_email = user
                user = User.query.filter_by(email=user_email).first()
                code = user.verification_code
                sub_code = request.form.get("code_conf")
                if code == sub_code:
                    return redirect(url_for("forgot_password", step="Password Reset", user=user_email))
            elif step == "Password Reset":
                salted_password = generate_password_hash(
                    password=request.form.get("password"),
                    method="pbkdf2:sha256",
                    salt_length=8
                )
                req_user = User.query.filter_by(email=user).first()
                req_user.password = salted_password
                db.session.commit()
                flash("Your password was successfully reset", category="reset_success")
                return redirect(url_for("login", reset_successful=True))

    return render_template("routes/main-site/forgot.html", form=form, year=year)


@app.route("/music-player", methods=["POST", "GET"])
def music_player():
    widget = request.args.get("widget")
    return render_template("routes/main-site/music-player.html", widget=widget)


@app.route("/song-upload", methods=["POST", "GET"])
@login_required
def song_upload():
    user = User.query.get(current_user.id)
    form = SongUpload(CombinedMultiDict((request.files, request.form)), meta={"csrf_context": flask.session})
    year = datetime.datetime.now().year
    is_authenticated = current_user.is_authenticated
    title = "Upload a new song | Andrew's Blog"
    if request.method == "POST":
        if form.validate():
            form_data = {
                "artist": form.artist.data,
                "album": form.album.data,
                "album_art": form.album_art.data,
                "song": form.song.data,
                "track_number": form.track_number.data
            }
            add_song = add_music(user, form_data)
            root_path = f"static/uploads/users/{user.id}-{user.name.replace(' ', '_').lower()}/data/music"
            artist_dir = f"{root_path}/{form_data['artist'].replace(' ', '_')}"
            album_dir = f"{artist_dir}/{form_data['album'].replace(' ', '_')}"
            album_art_filename = secure_filename(form_data["album_art"].filename)
            song_filename = secure_filename(form_data["song"].filename)
            if add_song:
                request.files['album_art'].save(os.path.join(album_dir, album_art_filename))
                request.files['song'].save(os.path.join(album_dir, song_filename))
                song = f"{form.song.data.filename}"
                song = song.replace(" ", "_")
                song_name = str(form_data["song"].filename)
                song_name = song_name[:-4]
                album_art = f"{form.album_art.data.filename}"
                album_art = album_art.replace(" ", "_")
                os.replace(f"{album_dir}/{song_filename}", f"{album_dir}/{song}")
                os.replace(f"{album_dir}/{album_art_filename}", f"{album_dir}/{album_art}")
                artist_obj = Artist.query.filter_by(artist=form_data["artist"]).first()
                album_obj = Album.query.filter_by(album=form_data["album"]).first()
                artist_exists = artist_obj
                if artist_exists:
                    album_exists = album_obj
                    if album_exists:
                        song_exists = Song.query.filter_by(song_name=song).first()
                        if song_exists:
                            flash("There was an issue uploading the song.\n"
                                  "Please verify that the song doesn't already exist and try again.")
                            return redirect(url_for("song_upload"))
                        else:
                            new_song = Song(
                                user=current_user,
                                artist=artist_obj,
                                album=album_obj,
                                album_art=f"{album_dir}/{album_art}",
                                song_file=f"{album_dir}/{song}",
                                song_name=song_name,
                                ref_id=secrets.token_hex(12),
                                track_number=form_data["track_number"]
                            )
                            db.session.add(new_song)
                            db.session.commit()
                            return redirect(url_for("profile", _id=user.id))
                    else:
                        new_song = Song(
                            user=current_user,
                            artist=artist_obj,
                            album=Album(artist=artist_obj, album=form_data["album"]),
                            album_art=f"{album_dir}/{album_art}",
                            song_file=f"{album_dir}/{song}",
                            song_name=song_name,
                            ref_id=secrets.token_hex(12),
                            track_number=form_data["track_number"]
                        )
                        db.session.add(new_song)
                        db.session.commit()
                        return redirect(url_for("profile", _id=user.id))
                else:
                    new_song = Song(
                        user=current_user,
                        artist=Artist(artist=form_data["artist"]),
                        album=Album(artist=artist_obj, album=form_data["album"]),
                        album_art=f"{album_dir}/{album_art}",
                        song_file=f"{album_dir}/{song}",
                        song_name=song_name,
                        ref_id=secrets.token_hex(12),
                        track_number=form_data["track_number"]
                    )
                    db.session.add(new_song)
                    db.session.commit()
                return redirect(url_for("profile", _id=user.id))
            else:
                flash("Song either already exists or there was an issue uploading the files\nPlease try again")
                return redirect(url_for("song_upload"))
    return render_template("routes/main-site/song-upload.html", form=form,
                           is_authenticated=is_authenticated,
                           title=title,
                           user=user,
                           year=year
                           )


@app.route("/remove-song", methods=["POST", "GET"])
@login_required
def remove_song():
    if int(request.args.get("id")) == current_user.id:
        deleted_song = delete_song(request.args.get("id"), request.args.get("song_id"))
        if not deleted_song[0]:
            flash(f"There was an error deleting song: {deleted_song[1]}", category="Deletion_Error")
            return redirect(url_for("settings", user_id=request.args.get("id")))
        else:
            flash(f"Track: {deleted_song[1]} was deleted", category="Deletion_Success")
            return redirect(url_for("settings", user_id=request.args.get("id")))
    else:
        flash("User ID doesn't match the current user's account ID.", category="Invalid")
        return redirect(url_for("settings", user_id=request.args.get("id")))


@app.route("/profile/settings", methods=["POST", "GET"])
@app.endpoint("settings")
@login_required
@fresh_login_required
def settings():
    user_id = request.args.get("user_id")
    title = "Settings | Andrew's Blog"
    year = datetime.datetime.now().year
    auth_user = User.query.get(user_id)
    form = ChangePassword(request.form, meta={"csrf_context": flask.session})
    all_users = query_users()
    song_query = get_user_songs(auth_user.id)
    if song_query is not False:
        user_songs = {song[0]: {"Artist": song[1], "Album": song[2], "Song": song[3], "Song File": song[4]}
                      for song in song_query}
    else:
        user_songs = None

    if request.method == "POST":
        if form.validate():
            user = User.query.get(current_user.id)
            salted_password = generate_password_hash(form.new_password.data, method="pbkdf2:sha256", salt_length=8)
            pass_check = check_password_hash(user.password, form.old_password.data)
            if pass_check:
                user.password = salted_password
                db.session.commit()
                flash("Password changed successfully.", category="Success")
                return redirect(url_for("settings", user_id=user.id, pass_change_success=True))
            else:
                flash("Current password doesn't match.", category="Incorrect")
                return redirect(url_for("settings", user_id=user.id, pass_change_success=False))
    elif current_user.id == auth_user.id:
        return render_template("routes/main-site/settings.html",
                               title=title,
                               user=auth_user,
                               user_songs=user_songs,
                               is_authenticated=current_user,
                               form=form,
                               year=year,
                               users=all_users,
                               current_user=current_user
                               )
    else:
        return abort(401)


@app.route("/profile/<int:user_id>/settings/edit", methods=["POST", "GET"])
@login_required
@fresh_login_required
def edit_settings(user_id):
    title = "Settings | Andrew's Blog"
    year = datetime.datetime.now().year
    auth_user = User.query.get(user_id)
    form = EditSettings(request.form, meta={"csrf_context": flask.session})
    if request.method == "POST" and form.validate():
        user = User.query.get(current_user.id)
        user.name = form.name.data
        user.email = form.email.data
        db.session.commit()
        return redirect(url_for("settings", user_id=user.id))
    form.name.data = auth_user.name
    form.email.data = auth_user.email
    return render_template("routes/main-site/settings-edit.html",
                           title=title,
                           user=auth_user,
                           is_authenticated=current_user,
                           year=year,
                           form=form
                           )


@app.route("/settings/admin/user-edit/<int:user_id>", methods=["POST", "GET"])
@login_required
@fresh_login_required
def user_edit(user_id):
    admin = current_user
    user_to_edit = User.query.get(user_id)
    year = datetime.datetime.now().year
    title = f"Editing {user_to_edit.name} | Andrew's Blog"
    form = EditUser(request.form, meta={"csrf_context": flask.session})
    form.name.data = user_to_edit.name
    form.email.data = user_to_edit.email
    form.account_type.data = user_to_edit.account_type
    user_dict = {
        "account_type": {"value": user_to_edit.account_type, "updated": False},
        "email": {"value": user_to_edit.email, "updated": False},
        "name": {"value": user_to_edit.name, "updated": False},
        "password": {"value": user_to_edit.password, "updated": False}
    }

    if request.method == "POST":
        if form.validate():
            for field in request.form.items():
                if field[0] == "csrf_token" or field[0] == "submit" or field[0] == "confirm":
                    continue
                else:
                    if user_dict[field[0]]["value"] != field[1]:
                        if field[0] == "password":
                            if field[1] == "":
                                continue
                            else:
                                user_dict[field[0]]["value"] = generate_password_hash(field[1], "pbkdf2:sha256", 8)
                                user_dict[field[0]]["updated"] = True
                        else:
                            user_dict[field[0]]["value"] = field[1]
                            user_dict[field[0]]["updated"] = True
            updated_data = update_account(user_to_edit, user_dict)
            if len(updated_data) > 0:
                flash(f"The following has been update for user id {user_to_edit.id}")
                for field in updated_data:
                    flash(f"• {field}")
                db.session.commit()
            else:
                flash(f"Nothing was updated")
            return redirect(url_for("settings", user_id=admin.id, user_updated=True))
    else:
        return render_template("routes/main-site/user-edit.html",
                               current_user=admin,
                               user=user_to_edit,
                               year=year,
                               title=title,
                               form=form
                               )


# ########## Random page and API routes ##########
@app.route("/random", methods=["POST", "GET"])
def random():
    title = "Random Stuff | Andrew's Blog"
    user = current_user
    year = datetime.datetime.now().year
    photo_data = apis.nasa()

    if request.method == "POST":
        pass
    else:
        return render_template("routes/main-site/random.html", title=title, year=year, user=user, nasa_data=photo_data)


@app.route("/random/apis/jokes", methods=["POST", "GET"])
def jokes():
    title = "Jokes | Andrew's Blog"
    user = current_user
    year = datetime.datetime.now().year
    script = ["js/jokesAPI.js"]

    return render_template("routes/api-pages/joke-api.html", title=title, year=year, user=user, scripts=script)


# ########## Guitar Tab Routes ##########
@app.route("/guitar-tabs", methods=["POST", "GET"])
@login_required
def guitar_tabs():
    title = "Guitar Tabs | Andrew's Guitar Tabs"
    all_artists = get_all_artists_tabs()
    return render_template("routes/guitar-tabs/guitar-tabs.html", title=title, all_artists=all_artists)


@app.route("/guitar-tabs/Guitar-Tab", methods=["POST", "GET"])
@login_required
def tab():
    artist = request.args.get('artist')
    song_name = request.args.get("song_name")
    title = f"{song_name} | Andrew's Guitar Tabs"
    song_file = get_song(artist, song_name)
    return render_template("routes/guitar-tabs/song-tab.html", title=title, artist=artist, songFile=song_file)


@app.route("/guitar-tabs/tab-upload", methods=["POST", "GET"])
@login_required
def tab_upload():
    title = "Tab Upload | Andrew's Guitar Tabs"
    form = TabUpload(CombinedMultiDict((request.files, request.form)), meta={"csrf_context": flask.session})
    if request.method == "POST" and form.validate():
        form_data = {
            'artist': form.artist.data,
            'album': form.album.data,
            'tab_name': form.song_name.data,
            'tab_file': form.song_file.data.filename
        }
        can_upload = upload_tab(form_data)
        if can_upload:
            file_dir = f"static/uploads/tab-files/{form_data['artist']}/{form_data['album']}"
            tab_file = secure_filename(request.files['song_file'].filename)
            request.files['song_file'].save(os.path.join(file_dir, tab_file))
            os.rename(f"{file_dir}/{form_data['tab_file'].replace(' ', '_')}", f"{file_dir}/{form_data['tab_file']}")
            return redirect(url_for("guitar_tabs"))
        else:
            flash("Unable to upload tab, please try again or contact an admin")
            return redirect(url_for("tab_upload"))
    else:
        return render_template("routes/guitar-tabs/tab-upload.html", title=title, form=form)


@app.route("/guitar-tabs/Artist/<string:artist>", methods=["POST", "GET"])
@login_required
def artist_index(artist):
    title = f"{artist} | Andrew's Guitar Tabs"
    all_songs = get_all_song_tabs(artist)
    return render_template("routes/guitar-tabs/artist.html", artist=artist, title=title, all_songs=all_songs)


# ################## Fetch Routes ##################
@app.route("/search-articles", methods=["POST", "GET"])
def search_articles():
    kw = request.args.get("q")
    sort = request.args.get("sort_by")
    amt = request.args.get("amount")
    data = apis.news(kw, sort, amt)
    if not session.get("articles"):
        session["articles"] = data
    else:
        session["articles"] = data
    articles = {"articles": data}
    return articles


@app.route("/get-jokes", methods=["POST", "GET"])
def get_jokes():
    url = request.args.get("url")
    all_jokes = apis.jokes(url)
    if all_jokes is not False:
        return all_jokes


@app.route("/fetch-artists", methods=["POST", "GET"])
def get_artists():
    all_artists = get_all_artists_audio()
    return all_artists


@app.route("/fetch-albums", methods=["POST", "GET"])
def get_albums():
    artist_id = request.args.get("artist_id")
    albums = get_all_albums_audio(artist_id)
    all_albums = {}
    for i in range(0, len(albums)):
        all_albums[i] = {"id": albums[i]["id"], "album": albums[i]["album"]}
    return all_albums


@app.route("/fetch-album-songs", methods=["GET"])
def fetch_album_songs():
    album_id = request.args.get("album_id")
    songs = get_album_songs(album_id)
    all_songs = []
    for _id in songs.keys():
        all_songs.append({_id: songs[_id]})
    return {"songs": all_songs}


@app.route("/fetch-songs", methods=["POST", "GET"])
def fetch_songs():
    import random
    shuffled = request.args.get("shuffled")
    all_artists = get_all_artists_audio()
    all_songs = []
    for artist_id in all_artists.keys():
        songs = get_all_songs_audio(all_artists[artist_id])
        for key in songs.keys():
            all_songs.append({key: songs[key]})
    if shuffled == "true":
        random.shuffle(all_songs)
    return {"songs": all_songs}


@app.route("/fetch-song", methods=["POST", "GET"])
def fetch_song():
    ref_id = request.args.get("_id")
    song_data = get_song_audio(ref_id)
    return song_data


@app.route("/fetch-previous-next-tracks", methods=["GET"])
def fetch_previous_next_tracks():
    ref_id = request.args.get("refId")
    all_artists = get_all_artists_audio()
    all_songs = []
    track_info = {}
    for artist_id in all_artists.keys():
        songs = get_all_songs_audio(all_artists[artist_id])
        for k in songs.keys():
            all_songs.append({"ref_id": k, "song_name": songs[k]["song_name"]})
    for i in range(0, len(all_songs)):
        if all_songs[i]["ref_id"] == ref_id:
            if i == 0:
                track_info["previous_track"] = all_songs[len(all_songs) - 1]
                track_info["next_track"] = all_songs[i + 1]
            elif i == len(all_songs) - 1:
                track_info["previous_track"] = all_songs[i - 1]
                track_info["next_track"] = all_songs[0]
            else:
                track_info["previous_track"] = all_songs[i - 1]
                track_info["next_track"] = all_songs[i + 1]
    return track_info


# Fresh Login Function
@login_manager.needs_refresh_handler
def refresh():
    user_id = None
    _id = None
    post_id = None
    if request.args.get("user_id"):
        user_id = request.args.get("user_id")
    if request.args.get("post_id"):
        post_id = request.args.get("post_id")
    if request.args.get("_id"):
        _id = request.args.get("_id")

    flash("To protect your account, re-authentication is needed to access this page.")
    if user_id:
        return redirect(url_for("login", next=request.endpoint, user_id=user_id))
    elif post_id:
        return redirect(url_for("login", next=request.endpoint, post_id=post_id))
    elif _id:
        return redirect(url_for("login", next=request.endpoint, _id=_id))
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


@app.errorhandler(500)
def server_error(e):
    if current_user.is_authenticated:
        user = User.query.get(current_user.id)
    else:
        user = None
    return render_template(
        "aborts/server-error.html",
        error=e,
        is_authenticated=current_user.is_authenticated,
        user=user
    ), 500


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=False)
    # app.run(host='127.0.0.1', port=5000, debug=True)  # for testing
