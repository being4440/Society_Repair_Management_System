import mysql.connector
DB_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '1810',
    'database': 'central_society'
}
try:
    conn = mysql.connector.connect(**DB_config)
    print("Connected OK")
    conn.close()
except Exception as e:
    print("Connection error:", e)
