from __future__ import annotations

import sqlite3
from typing import Annotated, Iterator

from fastapi import Depends

from . import config
from .db import connect


def get_conn() -> Iterator[sqlite3.Connection]:
    conn = connect(config.DB_PATH)
    try:
        yield conn
    finally:
        conn.close()


Conn = Annotated[sqlite3.Connection, Depends(get_conn)]
