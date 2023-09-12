from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, SelectField
from wtforms.validators import DataRequired, URL, Email, Length  # pip install email-validator
from flask_ckeditor import CKEditorField


# ------------------- Blog-Form ----------------------------------
class CreatePostForm(FlaskForm):
    title = StringField("Blog Post Title", validators=[DataRequired()])
    subtitle = StringField("Subtitle", validators=[DataRequired()])
    author = StringField("Your Name", validators=[DataRequired()])
    img_url = StringField("Blog Image URL", validators=[DataRequired(), URL()])
    body = CKEditorField("Blog Content", validators=[DataRequired()])
    # author_name = StringField("Author name", validators=[DataRequired()])
    submit = SubmitField("Submit Post")


class RegisterForm(FlaskForm):
    email = StringField(label="Email", validators=[DataRequired(),
                                                   Length(min=6, message='Little short for an email address?'),
                                                   Email(message='That\'s an invalid email address.')])
    password = PasswordField(label="Password", validators=[DataRequired(),
                                                           Length(min=8, max=120, message='Field must be at least 8 characters long.')])
    name = StringField("Name", validators=[DataRequired()])
    submit = SubmitField("Register")


class LoginForm(FlaskForm):
    email = StringField(label="Email", validators=[DataRequired(),
                                                   Length(min=6, message='Little short for an email address?'),
                                                   Email(message='That\'s an invalid email address.')])
    password = PasswordField(label="Password", validators=[DataRequired(),
                                                           Length(min=8, max=120, message='Field must be at least 8 characters long.')])
    submit = SubmitField(label="Log In")


class CommentForm(FlaskForm):
    comment_text = CKEditorField("Comment", validators=[DataRequired()])
    submit = SubmitField("Comment")


# ------------------- Cafe-Form ----------------------------------
class CafeForm(FlaskForm):
    cafe = StringField(label='Cafe name', validators=[DataRequired()])
    location = StringField(label='Cafe Location on Google Maps (URL)', validators=[DataRequired(), URL()])
    open = StringField(label='Opening Time e.g. 8:00AM', validators=[DataRequired()])
    close = StringField(label='Closing Time e.g. 5:30PM', validators=[DataRequired()])
    coffee_rating = SelectField(label='Coffee Rating', choices=["☕", "☕☕", "☕☕☕", "☕☕☕☕", "☕☕☕☕☕"], validators=[DataRequired()])
    wifi_rating = SelectField(label='Wifi Strength Rating', choices=["✘", "💪", "💪💪", "💪💪💪", "💪💪💪💪", "💪💪💪💪💪"], validators=[DataRequired()])
    power_rating = SelectField(label='Power socket Availability', choices=["✘", "🔌", "🔌🔌", "🔌🔌🔌", "🔌🔌🔌🔌", "🔌🔌🔌🔌🔌"], validators=[DataRequired()])
    submit = SubmitField(label='Submit')


# ------------------- Movie-Form ----------------------------------
class FindMovieForm(FlaskForm):
    title = StringField(label='Movie Title', validators=[DataRequired()])
    submit = SubmitField(label='Add Movie')


class EditMovieForm(FlaskForm):
    rating = StringField(label='Your Rating Out of 10 e.g. 7.5')
    review = StringField(label='Your Review')
    submit = SubmitField(label='Done')
