from flask import render_template, redirect, flash, url_for, request, abort
from flask_login import login_user, logout_user, current_user, login_required

from . import app, db, bcrypt
from .forms import RegistrationForm, LoginForm, ProfileForm, PostForm
from .models import User, Post


@app.route('/')
def Home():
    posts = Post.query.all()
    return render_template('home.html', posts=posts)


@app.route('/post/<post_id>', methods=['POST', 'GET'])
def detail(post_id):
    post = Post.query.get_or_404(post_id)
    # if post.author != current_user:
    #     abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        db.session.commit()
        flash('Post updated', 'warning')
    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content
    # return redirect(url_for('detail', post_id=post.id))
    return render_template('detail.html', post=post, form=form)


@app.route('/register', methods=['GET', 'POST'])
def Register():
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_pass = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_pass)
        db.session.add(user)
        db.session.commit()
        login_user(user)
        flash('you registered successfully', 'success')
        return redirect(url_for('Home'))
        # return redirect('/')
    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def Login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember_me.data)
            flash('you logged in successfully', 'success')
            return redirect(url_for('Home'))
        else:
            flash('you are not login, try again', 'danger')
    return render_template('login.html', form=form)


@app.route('/logout')
@login_required
def Logout():
    logout_user()
    flash('you are logged out', 'danger')
    return redirect(url_for('Home'))


@app.route('/profile', methods=['POST', 'GET'])
@login_required
def Profile():
    form = ProfileForm()
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('your data updated', 'success')
        return redirect(url_for('Profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email

    return render_template('profile.html', form=form)


@login_required
@app.route('/creat/post', methods=['POST', 'GET'])
def creat_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(title=form.title.data, content=form.content.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Post Created', "success")
        return redirect(url_for('Home'))
    return render_template('post.html', form=form)


@app.route('/post/<int:post_id>/delete')
def delete(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('Post deleted', 'danger')
    return redirect(url_for('Home'))


@app.route('/post/<int:post_id>/update', methods=['POST', 'GET'])
def update(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(404)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        db.session.commit()
        flash('post updated', 'warning')
        return redirect(url_for('detail', post_id=post.id))
    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content
    return render_template('update.html', form=form)
