import os
from datetime import date
from flask import Flask, render_template, redirect, url_for, flash, abort
from flask_bootstrap import Bootstrap5
from flask_ckeditor import CKEditor
from sqlalchemy.orm import relationship
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, current_user, logout_user
from forms import CreatePostForm, RegisterForm, LoginForm, CommentForm
from functools import wraps
from flask_gravatar import Gravatar

app = Flask(__name__)
# app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
bootstrap = Bootstrap5(app)

db = SQLAlchemy()
# CREATE DATABASE
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog_posts_users.db'
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# db.init_app(app)

ckeditor = CKEditor(app)
gravatar = Gravatar(app, size=100, rating='g', default='retro', force_default=False, force_lower=False, use_ssl=False, base_url=None)

# CONNECT TO DB
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DB_URI", "sqlite:///blog_posts_users.db").replace("postgres://", "postgresql://", 1)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# Configure Flask-Login's Login Manager
login_manager = LoginManager()
login_manager.init_app(app)


# Create a user_loader callback
@login_manager.user_loader
def load_user(user_id):
    return db.get_or_404(User, user_id)


# CREATE TABLE IN DB
class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    name = db.Column(db.String(1000), nullable=False)

    # List of posts created by each user
    posts = relationship("BlogPost", back_populates="author")

    # ***************Parent Relationship*************#
    comments = relationship("Comment", back_populates="comment_author")


class BlogPost(db.Model):
    __tablename__ = "blog_posts"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True, nullable=False)
    subtitle = db.Column(db.String(250), nullable=False)
    date = db.Column(db.String(500), nullable=False)
    body = db.Column(db.Text, nullable=False)
    img_url = db.Column(db.String(250), nullable=False)
    # Create foreign key
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))

    # Each user create list of posts
    author = relationship("User", back_populates="posts")
    # ***************Parent Relationship*************#
    comments = relationship("Comment", back_populates="parent_post")


class Comment(db.Model):
    __tablename__ = "comments"
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    post_id = db.Column(db.Integer, db.ForeignKey("blog_posts.id"))

    # ***************Child Relationship*************#
    comment_author = relationship("User", back_populates="comments")
    parent_post = relationship("BlogPost", back_populates="comments")


with app.app_context():
    db.create_all()


# Create admin-only decorator
def admin_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # if id != 1, return abort 403 error
        if current_user.id != 1:
            return abort(403)
        return f(*args, **kwargs)

    return decorated_function


@app.route('/')
def home():
    posts = db.session.execute(db.select(BlogPost)).scalars().all()
    return render_template('blog.html', all_posts=posts, current_user=current_user)


@app.route('/register', methods=['GET', 'POST'])
def register():
    register_form = RegisterForm()
    if register_form.validate_on_submit():
        email = register_form.email.data
        # Find user by entered email
        blog_user = db.session.execute(db.select(User).where(User.email == email)).scalar()
        if blog_user:  # blog_user exists
            flash("You've already signed up with this email, log in instead!")
            return redirect(url_for('login'))

        hash_and_salted_password = generate_password_hash(
            password=register_form.password.data,
            method='pbkdf2:sha256',
            salt_length=8
        )
        new_blog_user = User()
        new_blog_user.email = register_form.email.data
        new_blog_user.name = register_form.name.data
        new_blog_user.password = hash_and_salted_password

        db.session.add(new_blog_user)
        db.session.commit()

        # Authenticate user with Flask Login
        login_user(user=new_blog_user)
        return redirect(url_for('home'))
    return render_template("blog_register.html", form=register_form, current_user=current_user)


@app.route('/login', methods=['GET', 'POST'])
def login():
    login_form = LoginForm()
    if login_form.validate_on_submit():
        email = login_form.email.data
        password = login_form.password.data
        # Find blog_user by entered email
        blog_user = db.session.execute(db.select(User).where(User.email == email)).scalar()

        # Email doesn't exist or password incorrect
        if not blog_user:
            flash("Email doesn't exist, try again!")
            return redirect(url_for('login'))
        # Check stored password hash against entered password which is incorrect
        elif not check_password_hash(blog_user.password, password):
            flash("Password is incorrect, try again!")
            return redirect(url_for('login'))
        # Email exists and password correct
        else:
            login_user(user=blog_user)
            return redirect(url_for('home'))

    return render_template("blog_login.html", form=login_form, current_user=current_user)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route('/post/<int:post_id>', methods=['GET', 'POST'])
def show(post_id):
    requested_post = db.get_or_404(BlogPost, post_id)
    comment_form = CommentForm()
    if comment_form.validate_on_submit():
        if not current_user.is_authenticated:
            flash("You need to log in or register to comment!")
            return redirect(url_for('login'))

        new_comment = Comment(
            text=comment_form.comment_text.data,
            comment_author=current_user,
            parent_post=requested_post
        )
        db.session.add(new_comment)
        db.session.commit()
    return render_template('blog_post.html', post=requested_post, form=comment_form, current_user=current_user)


@app.route('/new-post', methods=['GET', 'POST'])
@admin_only  # add a decorator so only an admin user can create new post
def add():
    create_form = CreatePostForm()
    if create_form.validate_on_submit():
        new_post = BlogPost(
            title=create_form.title.data,
            subtitle=create_form.subtitle.data,
            body=create_form.body.data,
            img_url=create_form.img_url.data,
            author=current_user,
            date=date.today().strftime("%B, %d, %Y")
        )
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for('home'))
    return render_template('blog_add.html', form=create_form, current_user=current_user)


@app.route('/edit-post/<int:post_id>', methods=['GET', 'POST'])
def edit(post_id):
    post = db.get_or_404(BlogPost, post_id)
    edit_form = CreatePostForm(
        title=post.title,
        subtitle=post.subtitle,
        img_url=post.img_url,
        author=post.author,
        body=post.body
    )
    if edit_form.validate_on_submit():
        post.title = edit_form.title.data
        post.subtitle = edit_form.subtitle.data
        post.img_url = edit_form.img_url.data
        post.author = current_user
        post.body = edit_form.body.data

        db.session.commit()
        return redirect(url_for('show', post_id=post.id))
    return render_template('blog_add.html', form=edit_form, is_edit=True, current_user=current_user)


@app.route('/delete/<int:post_id>')
@admin_only
def delete(post_id):
    post_to_delete = db.get_or_404(BlogPost, post_id)
    db.session.delete(post_to_delete)
    db.session.commit()
    return redirect(url_for('home'))


@app.route("/about")
def about():
    return render_template("blog_about.html", current_user=current_user)


@app.route("/contact")
def contact():
    return render_template("blog_contact.html", current_user=current_user)


if __name__ == "__main__":
    # app.run(debug=True, host='0.0.0.0', port=5001)
    app.run(debug=False)
