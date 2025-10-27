# seed_hash_passwords.py
import mysql.connector, hashlib

DB = {
    'host': 'localhost',
    'user': 'root',
    'password': '1810',
    'database': 'central_society'
}

def make_password_from_row(name, contact):
    if not name: name = ""
    first2 = name.strip()[:2].lower()
    last3 = contact[-3:] if contact and len(contact) >= 3 else (contact or "")
    return first2 + last3

def sha256(s): return hashlib.sha256(s.encode()).hexdigest()

con = mysql.connector.connect(**DB)
cur = con.cursor(dictionary=True)
cur.execute("SELECT  Admin_ID , Admin_Name , Email, Contact_No FROM society_admin")
rows = cur.fetchall()

for r in rows:
    plain = make_password_from_row(r['Admin_Name'], r['Contact_No'])
    h = sha256(plain)
    cur2 = con.cursor()
    cur2.execute("UPDATE society_admin SET password_hash=%s WHERE Admin_ID=%s", (h, r['Admin_ID']))
    con.commit()
    print(f"Updated {r['Admin_ID']}: plain='{plain}' hash='{h[:8]}...'")
    cur2.close()

cur.close(); con.close()
print("All Admin password_hash values updated.")
