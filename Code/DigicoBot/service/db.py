import contextlib
import os

import psycopg
from pgvector.psycopg import register_vector

from settings import S

_SCHEMA = os.path.join(os.path.dirname(__file__), 'schema.sql')


@contextlib.contextmanager
def get_conn():
    conn = psycopg.connect(S.db_dsn)
    try:
        register_vector(conn)
        yield conn
    finally:
        conn.close()


def apply_schema():
    with psycopg.connect(S.db_dsn, autocommit=True) as conn:
        conn.execute(open(_SCHEMA).read())
