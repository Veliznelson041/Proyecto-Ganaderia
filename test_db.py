import psycopg2

try:
    conn = psycopg2.connect(
        dbname="sigrams_db",
        user="sigrams_user",
        password="Nelson24",
        host="localhost",
        port="5432"
    )
    print("✅ Conexión exitosa a PostgreSQL")
    conn.close()
except Exception as e:
    print("❌ Error de conexión:", e)
