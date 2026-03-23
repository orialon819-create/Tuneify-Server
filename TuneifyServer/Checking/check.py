
import sqlite3


conn = sqlite3.connect('../tuneify.db')
cursor = conn.cursor()


cursor.execute("""INSERT INTO users (first_name, last_name, email, username, password)
            VALUES (?, ?, ?, ?, ?)
        """, ("fname", "lname", "alonori8@gmail.com", "oriA", 2008))

conn.commit()

cursor.execute("SELECT * FROM users")
rows = cursor.fetchall()

for row in rows:
    print(row)


conn.close()