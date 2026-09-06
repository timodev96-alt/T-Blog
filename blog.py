from flask import render_template, request, url_for, redirect, Blueprint , g
import functools
import sqlite3
from database import get_db
from auth import login_required

bp = Blueprint('Blog', __name__, url_prefix='/posts')

@bp.route('/')
def index():
    conn = get_db()
    posts = conn.execute('SELECT * FROM posts').fetchall()
    conn.close()
    return render_template('index.html', posts=posts)

@bp.route('/<int:post_id>')
def show(post_id):
    conn = get_db()
    post = conn.execute('SELECT * FROM posts WHERE id=?',(post_id,)).fetchone()
    conn.close()
    return render_template('show_posts.html', post=post)

@bp.route('/create', methods=['GET','POST'])
@login_required
def create():
    if request.method == 'POST':
        conn = get_db()
        title = request.form['title']
        body = request.form['body']
        conn.execute('INSERT INTO posts (title, body, author_id) VALUES (?,?,?)', (title, body, g.user['id']))
        conn.commit()
        conn.close()
        return redirect(url_for('Blog.index'))

    return render_template('create_post.html')
