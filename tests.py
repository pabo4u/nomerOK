import sqlite3
import re

t = "id124"
t = re.findall(r"\d{1,6}", t)[0]

print(t)
