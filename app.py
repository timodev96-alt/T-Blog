import sqlite3
from flask import Flask, request, redirect, url_for, render_template, flash, session, g
from werkzeug.security import generate_password_hash, check_password_hash
import functools
from blog import bp as blogbp
from auth import bp as authbp

app = Flask(__name__)

app.config.from_mapping(SECRET_KEY = 'yeahbuddythisisjusttempone')

app.register_blueprint(blogbp)
app.register_blueprint(authbp)

app.add_url_rule('/', endpoint='Blog.index')