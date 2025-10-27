# db.py
import mysql.connector
from mysql.connector import Error
from config import DB_config
from utils import hash_password
from datetime import date

def get_connection():
    return mysql.connector.connect(**DB_config)

# Authentication helpers
def verify_resident_login(resident_id, password):
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT Resident_ID, Resident_Name, password_hash FROM resident WHERE Resident_ID=%s", (resident_id,))
    row = cur.fetchone()
    cur.close(); conn.close()
    if not row: 
        return None
    if row['password_hash'] == hash_password(password):
        return {'Resident_ID': row['Resident_ID'], 'Resident_Name': row['Resident_Name']}
    return None

def verify_admin_login(admin_id, password):
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT Admin_ID, Admin_Name, password_hash FROM society_admin WHERE Admin_ID=%s", (admin_id,))
    row = cur.fetchone()
    cur.close(); conn.close()
    if not row:
        return None
    if row['password_hash'] == hash_password(password):
        return {'Admin_ID': row['Admin_ID'], 'Admin_Name': row['Admin_Name']}
    return None

# Resident registration (simple)
def register_resident(resident_id, name, email, contact, block_name, flat_no, password):
    conn = get_connection()
    cur = conn.cursor()
    pwd_hash = hash_password(password)
    try:
        cur.execute("""
            INSERT INTO resident (Resident_ID, Resident_Name, Email, Contact_No, Block_name, Flat_No, password_hash)
            VALUES (%s,%s,%s,%s,%s,%s,%s)
        """, (resident_id, name, email, contact, block_name, flat_no, pwd_hash))
        conn.commit()
        return True, "Registered"
    except Error as e:
        return False, str(e)
    finally:
        cur.close(); conn.close()

# CRUD: personnel
def list_personnel():
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT Personnel_ID, Personnel_Name, Email, Contact_No, Specialization, Is_Available FROM repair_personnel")
    rows = cur.fetchall()
    cur.close(); conn.close()
    return rows

def add_personnel(pid, name, email, contact, specialization):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            INSERT INTO repair_personnel (Personnel_ID, Personnel_Name, Email, Contact_No, Specialization, Is_Available)
            VALUES (%s,%s,%s,%s,%s,1)
        """, (pid, name, email, contact, specialization))
        conn.commit()
        return True, "Personnel added"
    except Error as e:
        return False, str(e)
    finally:
        cur.close(); conn.close()

def set_personnel_availability(pid, available):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("UPDATE repair_personnel SET Is_Available=%s WHERE Personnel_ID=%s", (1 if available else 0, pid))
        conn.commit()
        return True, "Updated"
    except Error as e:
        return False, str(e)
    finally:
        cur.close(); conn.close()

# Requests
def create_repair_request(request_id, resident_id, issue_description, req_date=None):
    if req_date is None:
        req_date = date.today()
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            INSERT INTO repair_request
            (Request_ID, Resident_ID, Req_Status, Issue_Description, Req_Date)
            VALUES (%s,%s,%s,%s,%s)
        """, (request_id, resident_id, 'Pending', issue_description, req_date))
        conn.commit()
        return True, "Request created"
    except Error as e:
        return False, str(e)
    finally:
        cur.close(); conn.close()

def get_requests_for_resident(resident_id):
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("""
        SELECT r.Request_ID, r.Req_Status, r.Issue_Description, r.Req_Date, r.Completion_Date, p.Personnel_Name
        FROM repair_request r
        LEFT JOIN repair_personnel p ON r.Personnel_ID = p.Personnel_ID
        WHERE r.Resident_ID=%s
        ORDER BY r.Req_Date DESC
    """, (resident_id,))
    rows = cur.fetchall()
    cur.close(); conn.close()
    return rows

def get_all_requests():
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("""
        SELECT r.Request_ID, r.Resident_ID, res.Resident_Name, r.Personnel_ID, p.Personnel_Name, r.Req_Status, r.Issue_Description, r.Req_Date, r.Completion_Date
        FROM repair_request r
        LEFT JOIN repair_personnel p ON r.Personnel_ID = p.Personnel_ID
        LEFT JOIN resident res ON r.Resident_ID = res.Resident_ID
        ORDER BY r.Req_Date DESC
    """)
    rows = cur.fetchall()
    cur.close(); conn.close()
    return rows

def assign_personnel_to_request(request_id, personnel_id):
    conn = get_connection()
    cur = conn.cursor()
    try:
        # assign personnel
        cur.execute("UPDATE repair_request SET Personnel_ID=%s, Req_Status=%s WHERE Request_ID=%s", (personnel_id, 'Assigned', request_id))
        # mark personnel not available
        cur.execute("UPDATE repair_personnel SET Is_Available=0 WHERE Personnel_ID=%s", (personnel_id,))
        conn.commit()
        return True, "Assigned"
    except Error as e:
        return False, str(e)
    finally:
        cur.close(); conn.close()

def update_request_status(request_id, status, completion_date=None):
    conn = get_connection()
    cur = conn.cursor()
    try:
        if completion_date:
            cur.execute("UPDATE repair_request SET Req_Status=%s, Completion_Date=%s WHERE Request_ID=%s", (status, completion_date, request_id))
        else:
            cur.execute("UPDATE repair_request SET Req_Status=%s WHERE Request_ID=%s", (status, request_id))
        # if closed or completed, free personnel
        if status.lower() in ('completed', 'closed', 'resolved'):
            # find personnel and free them
            cur.execute("SELECT Personnel_ID FROM repair_request WHERE Request_ID=%s", (request_id,))
            pid = cur.fetchone()
            if pid and pid[0]:
                cur.execute("UPDATE repair_personnel SET Is_Available=1 WHERE Personnel_ID=%s", (pid[0],))
        conn.commit()
        return True, "Status updated"
    except Error as e:
        return False, str(e)
    finally:
        cur.close(); conn.close()
