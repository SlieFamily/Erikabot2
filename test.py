import re
import sqlite3

db = sqlite3.connect('db/anas.db')
cur = db.cursor()
cur.execute(f'''select * from "_爆点" where ana like "%爆点%"''')
print(cur.fetchall())