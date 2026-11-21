
import sqlite3

DATABASE_NAME = "jansahayak.db"


def create_database():
    connection = sqlite3.connect(DATABASE_NAME)

    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question TEXT,
            answer TEXT,
            language TEXT
        )
    """)

    connection.commit()
    connection.close()


def save_history(question, answer, language):
    connection = sqlite3.connect(DATABASE_NAME)

    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO history (question, answer, language)
        VALUES (?, ?, ?)
    """, (question, answer, language))

    connection.commit()
    connection.close()


def get_history():
    connection = sqlite3.connect(DATABASE_NAME)

    cursor = connection.cursor()

    cursor.execute("SELECT * FROM history ORDER BY id DESC")

    records = cursor.fetchall()

    connection.close()

    return records
