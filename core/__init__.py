import sqlite3
from core.utils.logging import Logging
from core.utils.functions import UserHandler
import os

log = Logging()

for file in ['extensions', 'temp']:
    if not os.path.exists(file):
        os.makedirs(file)
        

with open('core/utils/database.sql', 'r') as f:
    sql = f.read()
    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()
    cursor.executescript(sql)
    conn.commit()
    conn.close()

    log.log("Database initialized successfully", "success")

if UserHandler().create_user('admin', 'admin', 'John', 'Doe', 'admin') == True:
    log.log("Default user created successfully", "info")
    log.log("Username: admin", "info")
    log.log("Password: admin", "info")
