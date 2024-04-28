import sqlite3
import time

t = time.strftime("%m-%Y", time.localtime())
t_add = time.strftime("%d-%m-%Y, %H:%M:%S", time.localtime())

conn = sqlite3.connect(f'data/DataBases/history-{t}.db')
c = conn.cursor()
c.execute("CREATE TABLE IF NOT EXISTS History (id INTEGER PRIMARY KEY, time TEXT, number TEXT, route INTEGER) ")
c.execute('INSERT INTO History (time, number, route) VALUES (?, ?, ?)', (t_add, 'number', 0))

res = c.execute("SELECT * FROM History WHERE number=? ORDER BY time DESC", ("number",)).fetchone()

print(res)

conn.commit()
conn.close()