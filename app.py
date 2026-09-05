import sqlite3
from flask import Flask

app = Flask(__name__)

DATABASE = 'Blog.db'
def get_db():
    db = sqlite3.connect(DATABASE)
    db.row_factory = sqlite3.Row
    return db

@app.route('/posts')
def index():
    conn = get_db()
    posts = conn.execute('SELECT * FROM posts').fetchall()
    conn.close()
    posts_list = ['<ul>']
    for post in posts:
        post_title = f"""
            <li><a href="/posts/{post['id']}">{post['title']}</a></li>
        """
        posts_list.append(post_title)
    posts_list.append('</ul>')
    return ''.join(posts_list)

@app.route('/posts/<int:post_id>')
def show(post_id):
    conn = get_db()
    post = conn.execute('SELECT * FROM posts WHERE id=?',(post_id,)).fetchone()
    return f"""
        <h1>{post['title']}</h1>
        <p>{post['body']}</p>
    """