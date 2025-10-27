import mysql.connector
DB_config = {
    'host': 'localhost',
    'user': 'user_name',
    'password': 'your_password',
    'database': 'central_society'
}
try:
    conn = mysql.connector.connect(**DB_config)
    print("Connected OK")
    conn.close()
except Exception as e:
    print("Connection error:", e)
