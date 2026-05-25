import mysql.connector


def connection():
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Actowiz",
        database="FastApi"
    )

    cur = conn.cursor()

    return conn,cur

def create_user_db():
    conn,cur = connection()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users(
                u_id INT PRIMARY KEY,
                username VARCHAR(255),
                password VARCHAR(255),
                email VARCHAR(255) UNIQUE,
                age INT
                )
    """)
    conn.commit()
    conn.close()


create_user_db()