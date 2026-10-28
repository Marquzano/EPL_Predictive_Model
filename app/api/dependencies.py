import sqlite3
from fastapi import Request

def get_con(request: Request):
    con = sqlite3.connect(request.state.db_path, check_same_thread=False)
    try:
        yield con
    finally:
        con.close()