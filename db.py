import sqlite3

def init_db():
    conn = sqlite3.connect("resumes.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS evaluations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        resume_name TEXT,
        jd_name TEXT,
        score INTEGER,
        verdict TEXT,
        missing_skills TEXT,
        feedback TEXT
    )
    """)

    conn.commit()
    conn.close()
    print("✅ Database initialized successfully!")
