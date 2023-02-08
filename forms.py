from flask_wtf.file import FileAllowed
from wtforms import Form, StringField, SubmitField, PasswordField, SelectField, BooleanField, HiddenField, FileField
from wtforms.validators import DataRequired, URL, Email, EqualTo, Length, InputRequired
from wtforms.csrf.session import SessionCSRF
from flask_ckeditor import CKEditorField
from dotenv import dotenv_values
from datetime import timedelta
import os
config = dotenv_values(".env")


class MyBaseForm(Form):
    class Meta:
        csrf = True
        csrf_class = SessionCSRF
        csrf_secret = bytearray(config.get("SECRET_KEY"), 'utf-8')
        csrf_time_limit = timedelta(minutes=20)


# #WTForm
class CreatePostForm(MyBaseForm):
    title = StringField("Blog Post Title", validators=[DataRequired()])
    subtitle = StringField("Subtitle")
    img_url = StringField("Blog Image URL", validators=[DataRequired(), URL()])
    body = CKEditorField("Blog Content", validators=[DataRequired()])
    submit = SubmitField("Submit Post")


class RegisterForm(MyBaseForm):
    name = StringField("Name", validators=[DataRequired()])
    account_type = SelectField("Account Type", validators=[DataRequired()], choices=["Non-Admin"])
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[
        DataRequired(),
        EqualTo('confirm', message="Passwords must match")])
    confirm = PasswordField('Confirm Password')
    submit = SubmitField("Register")


class LoginForm(MyBaseForm):
    email = StringField("Email", validators=[DataRequired(message="This field is required"), Email(), InputRequired()])
    password = PasswordField("Password", validators=[DataRequired(message="Please enter a password"),
                                                     Length(min=6, max=35), InputRequired()])
    remember_me = BooleanField("Remember me")
    submit = SubmitField("Login")


class CommentForm(MyBaseForm):
    comment = CKEditorField(label="New Comment", validators=[DataRequired()])
    submit = SubmitField("Post")


class ContactForm(MyBaseForm):
    name = StringField("Name", validators=[DataRequired(message="Please enter a name")])
    email = StringField("Email", validators=[DataRequired(), Email("Please enter a valid email")])
    phone = StringField("Phone Number", validators=[Length(min=10, max=10, message="Must enter 10 digits")])
    message = CKEditorField("Message", validators=[DataRequired()])
    submit = SubmitField("Send")


class EmailPassword(MyBaseForm):
    step = HiddenField("")
    email = StringField("Email", validators=[DataRequired(), Email("Please enter a valid email")])
    submit = SubmitField("Submit")


class CodeConfirmation(MyBaseForm):
    step = HiddenField()
    code_conf = StringField("Enter Confirmation Code", validators=[DataRequired()])
    submit = SubmitField("Confirm")


class ResetPassword(MyBaseForm):
    step = HiddenField()
    password = PasswordField("New Password", validators=[DataRequired(), EqualTo("confirm", "Passwords must match")])
    confirm = PasswordField("Confirm")
    submit = SubmitField("Submit")


class ProfileContent(MyBaseForm):
    profile_picture = FileField("Profile Picture", validators=[FileAllowed(["jpg", "png"], "Images only!")])
    profile_bio = StringField("Profile Bio")
    submit = SubmitField("Update")


class SongUpload(MyBaseForm):
    artist = StringField("Artist", validators=[DataRequired()])
    album = StringField("Album", validators=[DataRequired()])
    album_art = FileField("Album Art", validators=[DataRequired(), FileAllowed(["jpg", "png"], "Images only!")])
    song = FileField("Song", validators=[FileAllowed(["wav", "mp3", "m4a"],
                                                     "Only .wav, .mp3, and .m4a files are accepted"),
                                         DataRequired()])
    track_number = SelectField("Track Number", choices=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10,
                                                    11, 12, 13, 14, 15, 16, 17, 18, 19, 20])
    submit = SubmitField("Upload")


class EditSettings(MyBaseForm):
    name = StringField("Name", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired(), Email("Please enter a valid email")])
    submit = SubmitField("Save")


class ChangePassword(MyBaseForm):
    old_password = PasswordField("Current Password", validators=[DataRequired()])
    new_password = PasswordField("New Password", validators=[DataRequired(),
                                                             EqualTo("confirm", "Passwords must match")
                                                             ])
    confirm = PasswordField("Confirm", validators=[DataRequired()])
    submit = SubmitField("Change Password")


class EditUser(MyBaseForm):
    name = StringField("Name")
    email = StringField("Email", validators=[Email("Please enter a valid email")])
    account_type = SelectField("Account Type", choices=["Non-Admin", "Admin", "Super-Admin"])
    password = PasswordField("New Password", validators=[EqualTo("confirm", "Passwords must match")])
    confirm = PasswordField("Confirm")
    submit = SubmitField("Save Edits")


class TabUpload(MyBaseForm):
    artist = StringField("Artist", validators=[DataRequired()])
    album = StringField("Album", validators=[DataRequired()])
    song_name = StringField("Song Name", validators=[DataRequired()])
    song_file = FileField("Song File", validators=[DataRequired(), FileAllowed(["gp3", "gp4", "gp5", "gpx", "gp"],
                                                     "Only guitar-pro files are allowed")])
    premium_tab = BooleanField("Premium Tab")
    submit = SubmitField("Upload")