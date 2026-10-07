import os
import sqlite3
from flask import g

DATABASE = os.environ.get('DATABASE_URL', 'Blog.db')

def init_db(db):
    db.executescript('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            password TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE
        );

        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            slug TEXT UNIQUE NOT NULL
        );

        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            body TEXT NOT NULL,
            author_id INTEGER,
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            category_id INTEGER REFERENCES categories(id),
            FOREIGN KEY(author_id) REFERENCES users(id) ON DELETE CASCADE
        );

        -- Insert default categories if empty
        INSERT OR IGNORE INTO categories (id, name, slug) VALUES 
        (1, 'General', 'general'),
        (2, 'Tech', 'tech'),
        (3, 'Stories', 'stories');
    ''')
    db.commit()

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
        init_db(g.db)  # Ensures tables exist
    return g.db

def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()