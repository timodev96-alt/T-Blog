from flask import render_template, request, url_for, redirect, Blueprint , g, flash, abort
import functools
import sqlite3
import markdown
import bleach
from database import get_db
from auth import login_required

bp = Blueprint('Blog', __name__, url_prefix='/posts')

def get_post(post_id, check_author = True):
    post = get_db().execute('SELECT * FROM posts WHERE id=?', (post_id,)).fetchone()

    if post is None:
        abort(404, f'There is no post with id:{post_id}')
    if check_author and post['author_id'] != g.user['id']:
        abort(403)
    return post

def get_categories():
    return get_db().execute('SELECT * FROM categories ORDER BY name').fetchall()

ALLOWED_TAGS = [
    'p','br','strong','em','u','s','ul','ol','li','h1','h2','h3','h4','blockquote','code','pre','a','hr'
]
ALLOWED_ATTRS = {'a':['href','title','rel']}

def render_markdown(text):
    html = markdown.markdown(text, extensions=['fenced_code','tables'])
    return bleach.clean(html, tags=ALLOWED_TAGS,attributes=ALLOWED_ATTRS)

def reading_time(text):
    words = len(text.split())
    minutes = max(1, round(words/100))
    return minutes

@bp.route('/')
def index():
    conn = get_db()
    category_slug = request.args.get('category')
    if category_slug:
        posts = conn.execute('''
        SELECT posts.*, categories.name AS category_name, categories.slug AS category_slug
        FROM posts
        JOIN categories ON posts.categories.id = categories.id
        WHERE categories.slug = ?
        ORDER BY posts.id DESC
        ''',(category_slug,)).fetchall()
    else:
        posts = conn.execute('''
        SELECT posts.*, categories.name AS category_name, categories.slug AS category_slug
        FROM posts
        LEFT JOIN categories ON posts.category_id = categories.id
        ORDER BY posts.id DESC
        ''').fetchall()
    categories = get_categories()
    conn.close()
    return render_template('index.html', posts=posts, categories=categories, active_category=category_slug)

@bp.route('/<int:post_id>')
def show(post_id):
    post = get_post(post_id, check_author=False)
    rendered_body = render_markdown(post['body'])
    minutes = reading_time(post['body'])
    category = None
    if post['category_id']:
        category = get_db().execute('SELECT * FROM categories WHERE id=?', (post['category_id'],)).fetchone()
    return render_template(
        'show_posts.html',
        post=post,
        reading_time=minutes,
        rendered_body=rendered_body,
        category=category
    )

@bp.route('/create', methods=['GET','POST'])
@login_required
def create():
    categories = get_categories()
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        category_id = request.form.get('category_id') or None
        error = None

        if not title:
            error = 'Please Enter a Title'

        if error is not None:
            flash(error)
        else:
            conn = get_db()
            conn.execute('INSERT INTO posts (title, body, author_id, category_id) VALUES (?,?,?,?)', (title, body, g.user['id'], category_id))
            conn.commit()
            conn.close()
            return redirect(url_for('Blog.index'))

    return render_template('create_post.html', categories=categories)

@bp.route('/<int:post_id>/update', methods=['GET','POST'])
@login_required
def update(post_id):
    post = get_post(post_id)
    categories = get_categories()
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        category_id = request.form.get('category_id') or None
        error = None

        if not title:
            error = 'Please  Enter a Title'
        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute('UPDATE posts SET title = ?, body = ?,category_id = ? WHERE id = ?', (title,body,category_id,post_id))
            db.commit()
            db.close()
            return redirect(url_for('Blog.index'))
    return render_template('create_post.html', post=post, categories=categories)

@bp.route('/<int:post_id>/delete', methods=['POST'])
@login_required
def delete(post_id):
    post = get_post(post_id)
    db = get_db()
    db.execute('DELETE FROM posts WHERE id = ?', (post_id,))
    db.commit()
    db.close()
    return redirect(url_for('Blog.index'))