import sqlite3



def remove_duplicate_liked_playlists():
    conn = sqlite3.connect("../tuneify.db")
    cursor = conn.cursor()
    try:
        # 1. מוצאים את ה-ID של פלייליסט הלייקים הראשון (החוקי) עבור משתמש 6
        cursor.execute("""
            SELECT MIN(id) FROM playlists 
            WHERE user_id = 6 AND name = 'Liked Songs'
        """)
        original_id = cursor.fetchone()[0]

        if not original_id:
            print("לא נמצאו פלייליסטים של Liked Songs עבור משתמש 6.")
            return

        print(f"הפלייליסט המקורי שיישמר הוא ID: {original_id}")

        # 2. מוחקים את כל שאר פלייליסטי ה-Liked Songs של משתמש 6 שה-ID שלהם גדול יותר מהמקורי
        cursor.execute("""
            DELETE FROM playlists 
            WHERE user_id = 6 AND name = 'Liked Songs' AND id > ?
        """, (original_id,))

        deleted_count = cursor.rowcount
        conn.commit()

        print(f"הניקוי בוצע בהצלחה! נמחקו {deleted_count} פלייליסטים משוכפלים.")

    except Exception as e:
        print(f"שגיאה בזמן המחיקה: {e}")
    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    remove_duplicate_liked_playlists()