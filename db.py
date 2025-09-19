
# db.py
import sqlite3

def init_db():
    conn = sqlite3.connect("ovitrampas.db")
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS trampas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            provincia TEXT,
            municipio TEXT,
            barrio TEXT,
            area_salud TEXT,
            clave_ovitrampa TEXT UNIQUE,
            clave_manzana TEXT,
            direccion TEXT,
            ubicacion TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS registros (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            semana INTEGER,
            trampa_id INTEGER,
            estado TEXT,
            huevos INTEGER,
            usuario TEXT,
            fecha TIMESTAMP,
            FOREIGN KEY (trampa_id) REFERENCES trampas (id)
        )
    """)
    conn.commit()
    conn.close()

def authenticate_user(username, password):
    conn = sqlite3.connect("ovitrampas.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
    user = cursor.fetchone()
    conn.close()
    return user

def register_user(username, password):
    conn = sqlite3.connect("ovitrampas.db")
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
    except sqlite3.IntegrityError:
        pass
    conn.close()
