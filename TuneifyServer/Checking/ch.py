import sqlite3

# Connect to your database
conn = sqlite3.connect("../tuneify.db")
cursor = conn.cursor()

# Correct SQL execution
cursor.execute("""
    UPDATE songs
    SET mood = 'Angry'
    WHERE LOWER(artist) = LOWER('Olivia Rodrigo')
""")

# Save changes
conn.commit()

print("good!")
# Close connection
conn.close()