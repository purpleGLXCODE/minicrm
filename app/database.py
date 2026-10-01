"""Minimal PostgreSQL connection for MiniCRM."""

import os

import psycopg
from dotenv import load_dotenv
from psycopg.rows import dict_row

load_dotenv()


db = psycopg.connect(
    host=os.getenv("DB_HOST"),
    dbname=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASS"),
    port=os.getenv("DB_PORT"),
    row_factory=dict_row,
)

db.autocommit = True


def sql(query, args=None):
    with db.cursor() as cur:
        cur.execute(query, args or [])
        return cur


def one(query, args=None):
    with db.cursor() as cur:
        cur.execute(query, args or [])
        return cur.fetchone()


def all(query, args=None):
    with db.cursor() as cur:
        cur.execute(query, args or [])
        return cur.fetchall()
