import functools
from flask import Blueprint, request, redirect, render_template, url_for, flash, session, g
from werkzeug.security import generate_password_hash, check_password_hash

from database import get_db, IntegrityError

bp = Blueprint('auth', __name__)


def login_required(func):
    @functools.wraps(func)
    def wrapped_func(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))
        return func(**kwargs)
    return wrapped_func


@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')
    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
        if g.user is None:
            session.clear()


@bp.route('/register', methods=['GET', 'POST'])
def register():
    if g.user:
        return redirect(url_for('Blog.index'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        error = None

        if not username:
            error = 'Please enter a username.'
        elif not email:
            error = 'Please enter an e-mail.'
        elif not password:
            error = 'Please enter a password.'
        elif len(password) < 6:
            error = 'Password must be at least 6 characters.'

        if error is None:
            db = get_db()
            try:
                db.execute(
                    'INSERT INTO users (username, email, password) VALUES (?, ?, ?)',
                    (username, email, generate_password_hash(password))
                )
                db.commit()
            except IntegrityError:
                db.rollback()
                error = 'That e-mail is already registered.'
            else:
                flash('Account created! Please log in.', 'success')
                return redirect(url_for('auth.login'))

        flash(error, 'danger')

    return render_template('auth/register.html')


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if g.user:
        return redirect(url_for('Blog.index'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        user = get_db().execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()

        if user is None or not check_password_hash(user['password'], password):
            flash('Wrong e-mail or password.', 'danger')
        else:
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('Blog.index'))

    return render_template('auth/login.html')


@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('Blog.index'))