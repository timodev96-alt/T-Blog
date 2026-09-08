from flask import Blueprint,request, redirect, render_template, url_for, flash, session, g
from werkzeug.security import generate_password_hash, check_password_hash
import functools
import sqlite3

from database import get_db

bp = Blueprint('auth',__name__)

def login_required(func):
    @functools.wraps(func)
    def wrapped_func(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))
        return func(**kwargs)
    return wrapped_func

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        error = None

        if not username:
            error = 'Please Enter a Username'
        if not email:
            error = 'Please Enter an E-mail'
        if not password:
            error = 'please Enter a Password'

        if error == None:
            db = get_db()
            try:
                db.execute(
                    'INSERT INTO users (username, email, password) VALUES (?,?,?)',
                    (username, email, generate_password_hash(password))
                )
                db.commit()
            except sqlite3.IntegrityError:
                error = f'{username} Username is already registered!'
            finally:
                db.close()
            if error is None:
                return redirect(url_for('auth.login'))
            if error:
                flash(error)

    return render_template('auth/register.html')

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        error = None
        db = get_db()
        user = db.execute('SELECT * FROM users WHERE email=?', (email,)).fetchone()
        db.close()

        if g.user:
            return redirect(url_for('Blog.index'))

        if user is None:
            error = "Email isn't registered!"
        elif not check_password_hash(user['password'],password):
            error = 'Wrong Password!'
        if error is None:
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('Blog.index'))
        flash(error)

    return render_template('auth/login.html')

@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')
    if user_id == None:
        g.user = None
    else:
        g.user = get_db().execute('SELECT * FROM users WHERE id=?', (user_id,)).fetchone()

@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('Blog.index'))
