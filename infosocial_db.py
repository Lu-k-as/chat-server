import psycopg
from psycopg.rows import dict_row
from model_infosocial import *

CONNECTINGSTRING  = 'postgres://postgres:PASSWORD@localhost:5432/gdi_ws2022_blatt3'

def db_connect_postgresql(connectstring='postgres://user:pw@localhost:port/dbname'):
    db_connection = psycopg.connect(connectstring, row_factory=dict_row)
    db_cursor = db_connection.cursor()
    db_connection.autocommit = True
    return db_connection, db_cursor


def db_close_db(db_connection, db_cursor):
    db_cursor.close()
    db_connection.close()
    return


def db_logged_in(infonaut):
    try:
        (db_connection, db_cursor) = db_connect_postgresql(CONNECTINGSTRING)
        db_cursor.execute("SELECT COUNT(*) FROM infonauts WHERE name=%(name)s", {"name": infonaut})
        if(db_cursor.fetchall()[0]["count"]):
            db_cursor.execute("UPDATE infonauts SET last_login= CURRENT_TIMESTAMP WHERE name=%(name)s", {"name": infonaut})
            db_close_db(db_connection, db_cursor)
            return True
        else:
            db_cursor.execute("INSERT INTO infonauts VALUES (%(name)s,CURRENT_TIMESTAMP)", {"name": infonaut})
            db_close_db(db_connection, db_cursor)
            return True
    except psycopg.DatabaseError as error:
        print("Error", error)
    db_close_db(db_connection, db_cursor)
    return False


def db_load_all_infos(infonaut):
    try:
        ls = []
        (db_connection, db_cursor) = db_connect_postgresql(CONNECTINGSTRING)
        query = """SELECT tmp.id, tmp.creator, tmp.text, tmp.creation_date, tmp.likes, COUNT(l1.infonaut) AS self_like
                FROM(
                SELECT i.id, i.creator, i.text, i.creation_date, COUNT(l.infonaut) AS likes 
                FROM infos i LEFT OUTER JOIN likes l ON(i.id = l.infos) 
                GROUP BY i.id, i.creator, i.text, i.creation_date 
                ORDER BY i.creation_date DESC
                )tmp LEFT OUTER JOIN likes l1 ON(tmp.id = l1.infos AND tmp.creator=l1.infonaut) 
                GROUP BY tmp.id, tmp.creator, tmp.text, tmp.creation_date, tmp.likes
                ORDER BY tmp.creation_date DESC;
                """
        db_cursor.execute(query)
        row = db_cursor.fetchone()
        while row is not None:
            data = Info(row["id"], row["creator"], row["text"], row["creation_date"], row["likes"], row["self_like"])
            ls.append(data)
            row = db_cursor.fetchone()
        db_close_db(db_connection, db_cursor)
        return ls
    except psycopg.DatabaseError as error:
        print("Error", error)
        exept = ItWasntMe()
        raise exept
    db_close_db(db_connection, db_cursor)
    return []


def db_create_info(infonaut, text):
    try:
        (db_connection, db_cursor) = db_connect_postgresql(CONNECTINGSTRING)
        query = "SELECT MAX(id) FROM infos;"
        db_cursor.execute(query)
        row = db_cursor.fetchone()
        db_cursor.execute("INSERT INTO infos VALUES (%(id)s,%(creator)s,%(text)s,CURRENT_TIMESTAMP);", {"id": row["max"]+1, "creator": infonaut, "text": text})
        db_close_db(db_connection, db_cursor)
        return True
    except psycopg.DatabaseError as error:
        print("Error", error)
    db_close_db(db_connection, db_cursor)
    return False


def db_delete_info(infonaut, info_id):
    try:
        (db_connection, db_cursor) = db_connect_postgresql(CONNECTINGSTRING)
        db_cursor.execute("SELECT COUNT(*) FROM infos WHERE creator=%(name)s AND id =%(id)s", {"name": infonaut, "id": info_id})
        if(db_cursor.fetchall()[0]["count"]):
            db_cursor.execute("DELETE FROM infos WHERE creator=%(name)s AND id =%(id)s", {"name": infonaut, "id": info_id})
            db_close_db(db_connection, db_cursor)
            return True
        else:
            db_close_db(db_connection, db_cursor)
            return True
    except psycopg.DatabaseError as error:
        print("Error", error)
    db_close_db(db_connection, db_cursor)
    return False


def db_like(infonaut, info_id):
    try:
        (db_connection, db_cursor) = db_connect_postgresql(CONNECTINGSTRING)
        db_cursor.execute("SELECT COUNT(*) FROM infos WHERE creator=%(name)s AND id =%(id)s", {"name": infonaut, "id": info_id})
        if(db_cursor.fetchall()[0]["count"]):
            db_close_db(db_connection, db_cursor)
            return False
        else:
            db_cursor.execute("INSERT INTO likes VALUES (%(infos)s,%(infonaut)s);",
                              {"infos": info_id, "infonaut": infonaut})
            db_close_db(db_connection, db_cursor)
            return True
    except psycopg.DatabaseError as error:
        print("Error", error)
    db_close_db(db_connection, db_cursor)
    return False

