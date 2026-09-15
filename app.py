import os 
from flask import Flask
from database import close_db
from blog import bp as blogbp
from auth import bp as authbp

app = Flask(__name__)

app.config.from_mapping(
    SECRET_KEY = os.environ.get('SECRET_KEY', 'testtesttesttest')
)

UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENTIONS = {'png','jpg','jpeg','gif','pdf','txt','docx'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.teardown_appcontext(close_db)
app.register_blueprint(blogbp)
app.register_blueprint(authbp)

app.add_url_rule('/', endpoint='Blog.index')

if __name__ == "__main__" :
    app.run(debug=True)