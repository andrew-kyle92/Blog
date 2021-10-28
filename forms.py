from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, SelectField, BooleanField
from wtforms.validators import DataRequired, URL, Email, EqualTo, Length
from flask_ckeditor import CKEditorField


# #WTForm
class CreatePostForm(FlaskForm):
    title = StringField("Blog Post Title", validators=[DataRequired()])
    subtitle = StringField("Subtitle", validators=[DataRequired()])
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
