from mysql.connector import pooling
import keyring
import logging
import json

dbconfig = {
    "user": "auto1",
    "password": keyring.get_password("Database-Values", "db_auto1"),
    "host": "185.101.156.105",
    "database": "ai_texts"
}

pool = pooling.MySQLConnectionPool(
    pool_name="mypool",
    pool_size=5,
    **dbconfig
)


def insert_dict(table, data):
    try:
        cols = ", ".join(data.keys())
        placeholders = ", ".join(["'{}'"] * len(data))
        values = list(data.values())
        for i in range(len(values)):
            values[i] = values[i].replace("'", "\\'")
        placeholders = placeholders.format(*values)
        query = f"INSERT IGNORE INTO {table} ({cols}) VALUES ({placeholders})"
        return query
    except Exception as e:
        logging.exception(e)
        logging.info(json.dumps(data))
        return ""
