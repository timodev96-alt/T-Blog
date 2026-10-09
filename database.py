import os
import sqlite3
from flask import g

DATABASE_URL = os.environ.get('DATABASE_URL')
USE_PG = bool(DATABASE_URL)

if USE_PG:
    import psycopg2
    import psycopg2.extras
    IntegrityError = psycopg2.IntegrityError
else:
    IntegrityError = sqlite3.IntegrityError
    DATABASE = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'Blog.db')

PK = 'SERIAL PRIMARY KEY' if USE_PG else 'INTEGER PRIMARY KEY AUTOINCREMENT'

SCHEMA = f'''
CREATE TABLE IF NOT EXISTS users (
    id {PK},
    username TEXT NOT NULL,
    password TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE
);
CREATE TABLE IF NOT EXISTS categories (
    id {PK},
    name TEXT UNIQUE NOT NULL,
    slug TEXT UNIQUE NOT NULL
);
CREATE TABLE IF NOT EXISTS posts (
    id {PK},
    title TEXT NOT NULL,
    body TEXT NOT NULL,
    author_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    category_id INTEGER REFERENCES categories(id)
);
INSERT INTO categories (name, slug) VALUES
    ('General', 'general'), ('Tech', 'tech'), ('Stories', 'stories')
ON CONFLICT DO NOTHING;
'''

_initialized = False


class DB:
    def __init__(self, conn):
        self.conn = conn

    def execute(self, sql, params=()):
        if USE_PG:
            cur = self.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cur.execute(sql.replace('?', '%s'), params)
            return cur
        return self.conn.execute(sql, params)

    def commit(self):
        self.conn.commit()

    def rollback(self):
        self.conn.rollback()

    def close(self):
        self.conn.close()


def _init_schema(db):
    global _initialized
    if _initialized:
        return
    if USE_PG:
        db.conn.cursor().execute(SCHEMA)
    else:
        db.conn.executescript(SCHEMA)
    db.commit()
    _initialized = True


def get_db():
    if 'db' not in g:
        if USE_PG:
            conn = psycopg2.connect(DATABASE_URL)
        elif os.environ.get('VERCEL'):
            raise RuntimeError('DATABASE_URL is not set. SQLite cannot persist on Vercel.')
        else:
            conn = sqlite3.connect(DATABASE)
            conn.row_factory = sqlite3.Row
        g.db = DB(conn)
        _init_schema(g.db)
    return g.db


def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()