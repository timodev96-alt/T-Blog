import sqlite3
from flask import Flask, request, redirect, url_for, render_template, flash, session, g
from werkzeug.security import generate_password_hash, check_password_hash
import functools

app = Flask(__name__)

app.config.from_mapping(SECRET_KEY = 'yeahbuddythisisjusttempone')

DATABASE = 'Blog.db'
def get_db():
    db = sqlite3.connect(DATABASE)
    db.row_factory = sqlite3.Row
    return db

def login_required(func):
    @functools.wraps(func)
    def wrapped_func(**kwargs):
        if g.user is None:
            return redirect(url_for('login'))
        return func(**kwargs)
    return wrapped_func

@app.route('/posts')
def index():
    conn = get_db()
    posts = conn.execute('SELECT * FROM posts').fetchall()
    conn.close()
    return render_template('index.html', posts=posts)

@app.route('/posts/<int:post_id>')
def show(post_id):
    conn = get_db()
    post = conn.execute('SELECT * FROM posts WHERE id=?',(post_id,)).fetchone()
    conn.close()
    return render_template('show_posts.html', post=post)

@app.route('/posts/create', methods=['GET','POST'])
@login_required
def create():
    if request.method == 'POST':
        conn = get_db()
        title = request.form['title']
        body = request.form['body']
        conn.execute('INSERT INTO posts (title, body, author_id) VALUES (?,?,?)', (title, body, g.user['id']))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))

    return render_template('create_post.html')

@app.route('/register', methods=['GET', 'POST'])
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
                db.execute('INSERT INTO users (username, email, password) VALUES (?,?,?)', (username, email, generate_password_hash(password)))
                db.commit()
                db.close()
            except db.IntegrityError:
                error = f'{username} Username is already registered!'
            else:
                return redirect(url_for('login'))
            flash(error)

    return render_template('auth/register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        error = None
        db = get_db()
        user = db.execute('SELECT * FROM users WHERE email=?', (email,)).fetchone()
        db.close()

        if g.user:
            return redirect(url_for('index'))

        if user is None:
            error = "Email isn't registered!"
        elif not check_password_hash(user['password'],password):
            error = 'Wrong Password!'
        if error is None:
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('index'))
        flash(error)

    return render_template('auth/login.html')

@app.before_request
def load_logged_in_user():
    user_id = session.get('user_id')
    if user_id == None:
        g.user = None
    else:
        g.user = get_db().execute('SELECT * FROM users WHERE id=?', (user_id,)).fetchone()

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))
