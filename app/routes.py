from flask import render_template, flash, redirect, url_for
from app import app
from app.forms import LoginForm, RegistrationForm, MakePostForm, ReplyForm
from flask_login import current_user, login_user
from flask_login import logout_user
from app.models import User, Post, Reply
from flask_login import login_required
from flask import request
from werkzeug.urls import url_parse
from app import db


@app.route('/', methods=['GET', 'POST'])
@app.route('/homepage', methods=['GET', 'POST'])
def homepage():
    form = MakePostForm()
    if form.validate_on_submit():
        post = Post(title=form.title.data, desc=form.desc.data, user_id=current_user.id)
        db.session.add(post)
        db.session.commit()
        return render_template('homepage.html', title='Home', posts=Post.query.all(), form=form)
    return render_template('homepage.html', title='Home', posts=Post.query.all(), form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('homepage'))


@app.route('/tutorial')
def tutorial():
    return render_template('tutorialpage.html', title='Tutorial')


@app.route('/topicpage/<postid>', methods=['GET', 'POST'])
def topic(postid):
    myPost = Post.query.get(postid)
    form = ReplyForm()
    if form.validate_on_submit():
        reply = Reply(post_id=postid, text=form.text.data, stance=('True' == form.stance.data))
        db.session.add(reply)
        db.session.commit()
        myReply = Post.query.get(postid).p_replies.all()
        return render_template('topicpage.html', title='Topic', post = myPost, replies = myReply, form=form)
    myReply = Post.query.get(postid).p_replies.all()
    return render_template('topicpage.html', title='Topic', post = myPost, replies = myReply, form=form)


@app.route('/profile/<userid>')
def profile(userid):
    myUser = User.query.get(userid)
    return render_template('profile.html', title='Profile', user = myUser)


@app.route('/contact')
def contact():
    return render_template('contact.html', title='Contact')


@app.route('/signin', methods=['GET', 'POST'])
def signin():
    if current_user.is_authenticated:
        return redirect(url_for('homepage'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('signin'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('homepage')
        return redirect(next_page)
    return render_template('signin.html', title='Sign In', form=form)



@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        user.admin = False # user not admin by default
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('signin'))
    return render_template('signup.html', title='Sign Up', form=form)
