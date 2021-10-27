import datetime
import os
from datetime import date, time
import time as t

from email_class import SendEmail

from dotenv import dotenv_values
from flask import Flask, render_template, redirect, url_for, flash, request, abort, session
from flask.sessions import  SessionMixin
from flask_bootstrap import Bootstrap
from flask_ckeditor import CKEditor
from flask_gravatar import Gravatar
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from werkzeug.security import generate_password_hash, check_password_hash

from forms import CreatePostForm, RegisterForm, LoginForm, CommentForm, ContactForm


app = Flask(__name__)
config = dotenv_values(".env")
SECRET_KEY = os.urandom(32)  # This is for testing
app.config['SECRET_KEY'] = SECRET_KEY  # This is for testing
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
db = SQLAlchemy(app)

# #USER LOGIN
login_manager = LoginManager()
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
    email = db.Column(db.String(255), unique=True, nullable=False)
    name = db.Column(db.String(255), nullable=False)
    password = db.Column(db.String(255), nullable=False)
    posts = relationship("BlogPost", back_populates="author")
    comments = relationship("Comment", back_populates="author")


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
def get_all_posts():
    year = datetime.datetime.now().year
    if current_user:
        user = current_user
        # print(user.account_type)
    else:
        user = None
    posts = BlogPost.query.all()
    return render_template("index.html", all_posts=posts, is_authenticated=user.is_authenticated, user=user, year=year)


@app.route('/register', methods=["POST", "GET"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
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
                name=request.form.get("name"),
                password=salted_password
            )
            db.session.add(new_user)
            db.session.commit()

            login_user(new_user)

            return redirect(url_for("get_all_posts"))

    return render_template("register.html", form=form)


@app.route('/login', methods=["POST", "GET"])
def login():
    form = LoginForm()
    if request.method == "POST":
        if form.validate_on_submit():
            email = request.form.get("email")
            password = request.form.get("password")
            user = User.query.filter_by(email=email).first()

            if check_password_hash(user.password, password):
                login_user(user)
                return redirect(url_for("get_all_posts"))
            else:
                flash("Your username or password is incorrect", category="Unsuccessful_Login")
                return redirect(url_for("login"))
    return render_template("login.html", form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('get_all_posts'))


@app.route("/post/<int:post_id>", methods=["POST", "GET"])
def show_post(post_id):
    user = current_user
    requested_post = BlogPost.query.get(post_id)
    comments = Comment.query.all()
    form = CommentForm()
    struct_time = t.localtime(t.time())
    time_now = t.strftime("%I:%M %p", struct_time)
    # print(time_now)
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
        form=form
    )


@app.route("/about")
def about():
    user = current_user
    return render_template("about.html", is_authenticated=user.is_authenticated)


@app.route("/contact", methods=["POST", "GET"])
def contact():
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
        send_email.send_email(msg_info)
        flash(message="Your message was sent, successfully!", category="Email Sent Success")
        return redirect(url_for("contact"))
    return render_template("contact.html", is_authenticated=user.is_authenticated, form=form)


@app.route("/new-post", methods=["POST", "GET"])
@login_required
def add_new_post():
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
        return render_template("make-post.html", form=form, is_authenticated=user.is_authenticated, user=user)


@app.route("/edit-post/<int:post_id>", methods=["POST", "GET"])
@login_required
def edit_post(post_id):
    user = current_user
    post = BlogPost.query.get(post_id)
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
            user=user)
    else:
        print(f"User ID: {user.id}\nAuthor ID: {post.author_id}")
        return abort(401, response="aborts/forbidden.html")


@app.route("/delete/<int:post_id>")
@login_required
def delete_post(post_id):
    post_to_delete = BlogPost.query.get(post_id)
    db.session.delete(post_to_delete)
    db.session.commit()
    return redirect(url_for('get_all_posts'))


# Error Handling Functions

@app.errorhandler(401)
def forbidden(e):
    print(current_user.is_authenticated)
    return render_template("/aborts/forbidden.html", error=e, is_authenticated=current_user.is_authenticated), 401


@app.errorhandler(404)
def not_found(e):
    return render_template("/aborts/not-found.html", error=e, is_authenticated=current_user.is_authenticated), 404


if __name__ == "__main__":
    app.run(host='localhost', port=5000)
