import os
import sqlite3
from flask import Flask
from database import close_db
from blog import bp as blogbp
from auth import bp as authbp

base_dir = os.path.abspath(os.path.dirname(__file__))
app = Flask(
    __name__,
    template_folder=os.path.join(base_dir, 'templates'),
    static_folder=os.path.join(base_dir, 'static')
)

app.config.from_mapping(
    SECRET_KEY=os.environ.get('SECRET_KEY', 'WAODFWAWNAJDNPGAWDPKJWDIJAWD')
)

if os.environ.get('VERCEL'):
    UPLOAD_FOLDER = '/tmp/uploads'
else:
    UPLOAD_FOLDER = os.path.join(base_dir, 'static', 'uploads')

ALLOWED_EXTENTIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'txt', 'docx'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.teardown_appcontext(close_db)
app.register_blueprint(blogbp)
app.register_blueprint(authbp)

app.add_url_rule('/', endpoint='Blog.index')

@app.route('/dbcheck')
def dbcheck():
    import traceback
    try:
        from database import get_db
        get_db().execute('SELECT 1').fetchone()
        return 'DB OK'
    except Exception:
        return '<pre>' + traceback.format_exc() + '</pre>', 500

if __name__ == "__main__" :
    app.run(debug=True)