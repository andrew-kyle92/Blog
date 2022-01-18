from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed
from wtforms import StringField, SubmitField, PasswordField, SelectField, BooleanField, HiddenField, FileField
from wtforms.validators import DataRequired, URL, Email, EqualTo, Length
from flask_ckeditor import CKEditorField


# #WTForm
class CreatePostForm(FlaskForm):
    title = StringField("Blog Post Title", validators=[DataRequired()])
    subtitle = StringField("Subtitle")
    img_url = StringField("Blog Image URL", validators=[DataRequired(), URL()])
    body = CKEditorField("Blog Content", validators=[DataRequired()])
    submit = SubmitField("Submit Post")


class RegisterForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    account_type = SelectField("Account Type", validators=[DataRequired()], choices=["Non-Admin"])
    email = StringField("Email", validators=[DataRequired(), Email("Please enter a valid email")])
    password = PasswordField("Password", validators=[
        DataRequired(),
        EqualTo('confirm', message="Passwords must match")])
    confirm = PasswordField('Confirm Password')
    submit = SubmitField("Register")


class LoginForm(FlaskForm):
    next_url = HiddenField("next")
    email = StringField("Email", validators=[DataRequired(), Email("Please enter a valid email")])
    password = PasswordField("Password", validators=[DataRequired()])
    remember_me = BooleanField("Remember me")
    submit = SubmitField("Login")


class CommentForm(FlaskForm):
    comment = CKEditorField(label="New Comment", validators=[DataRequired()])
    submit = SubmitField("Post")


class ContactForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired(message="Please enter a name")])
    email = StringField("Email", validators=[DataRequired(), Email("Please enter a valid email")])
    phone = StringField("Phone Number", validators=[Length(min=10, max=10, message="Must enter 10 digits")])
    message = CKEditorField("Message", validators=[DataRequired()])
    submit = SubmitField("Send")


class EmailPassword(FlaskForm):
    step = HiddenField("Email Confirmation", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired(), Email("Please enter a valid email")])
    submit = SubmitField("Submit")


class CodeConfirmation(FlaskForm):
    step = HiddenField("Code Confirmation", validators=[DataRequired()])
    code = HiddenField("Code", validators=[DataRequired()])
    code_conf = StringField("Enter Confirmation Code", validators=[DataRequired()])
    submit = SubmitField("Confirm")


class ResetPassword(FlaskForm):
    step = HiddenField("Password Reset", validators=[DataRequired()])
    password = PasswordField("New Password", validators=[DataRequired(), EqualTo("confirm", "Passwords must match")])
    confirm = PasswordField("confirm")
    submit = SubmitField("Submit")


class ProfileContent(FlaskForm):
    profile_picture = FileField("Profile Picture", validators=[FileAllowed(["jpg", "png"], "Images only!")])
    profile_bio = StringField("Profile Bio")
    submit = SubmitField("Update")


class SongUpload(FlaskForm):
    artist = StringField("Artist", validators=[DataRequired()])
    album = StringField("Album", validators=[DataRequired()])
    album_art = FileField("Album Art", validators=[FileAllowed(["jpg", "png"], "Images only!")])
    song = FileField("Song", validators=[FileAllowed(["wav", "mp3", "m4a"],
                                                     "Only .wav, .mp3, and .m4a files are accepted")])
    submit = SubmitField("Submit")


class EditSettings(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired(), Email("Please enter a valid email")])
    submit = SubmitField("Save")


class ChangePassword(FlaskForm):
    old_password = PasswordField("Current Password", validators=[DataRequired()])
    new_password = PasswordField("New Password", validators=[DataRequired(),
                                                             EqualTo("confirm", "Passwords must match")
                                                             ])
    confirm = PasswordField("Confirm", validators=[DataRequired()])
    submit = SubmitField("Change Password")


class EditUser(FlaskForm):
    name = StringField("Name")
    email = StringField("Email", validators=[Email("Please enter a valid email")])
    account_type = SelectField("Account Type", choices=["Non-Admin", "Admin", "Super-Admin"])
    password = PasswordField("New Password", validators=[EqualTo("confirm", "Passwords must match")])
    confirm = PasswordField("Confirm")
    submit = SubmitField("Save Edits")