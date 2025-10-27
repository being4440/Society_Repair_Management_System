# main.py
import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
from mysql.connector import Error
import datetime
from config import DB_config
from utils import hash_password
from admin_ui import AdminFrame
from resident_ui import ResidentFrame
import random
import string

# ----------------- DB helpers -----------------
def get_connection_no_db():
    # connect without specifying database (used to create DB if missing)
    cfg = DB_config.copy()
    cfg2 = {k: v for k, v in cfg.items() if k != 'database'}
    return mysql.connector.connect(**cfg2)

def get_connection():
    return mysql.connector.connect(**DB_config)

def initialize_database():
    """Ensure 'society' database exists and required tables exist."""
    try:
        conn = get_connection_no_db()
        cursor = conn.cursor()
        cursor.execute("SHOW DATABASES LIKE %s", (DB_config['database'],))
        if not cursor.fetchone():
            print(f"Database `{DB_config['database']}` not found. Creating...")
            cursor.execute(f"CREATE DATABASE `{DB_config['database']}`")
            print("Database created.")
        cursor.close()
        conn.close()
    except Error as e:
        raise

    # now create tables if not exist
    conn = get_connection()
    cur = conn.cursor()
    # resident
    cur.execute("""
        CREATE TABLE IF NOT EXISTS resident(
            Resident_ID VARCHAR(8) PRIMARY KEY,
            Resident_Name VARCHAR(100),
            Email VARCHAR(100),
            Contact_No VARCHAR(20),
            Block_name VARCHAR(20),
            Flat_No INT,
            password_hash VARCHAR(128)
        )
    """)
    # society_admin
    cur.execute("""
        CREATE TABLE IF NOT EXISTS society_admin(
            Admin_ID VARCHAR(8) PRIMARY KEY,
            Admin_Name VARCHAR(100),
            Email VARCHAR(100),
            Contact_No VARCHAR(20),
            registration_no VARCHAR(30),
            password_hash VARCHAR(128)
        )
    """)
    # repair_personnel
    cur.execute("""
        CREATE TABLE IF NOT EXISTS repair_personnel(
            Personnel_ID VARCHAR(8) PRIMARY KEY,
            Personnel_Name VARCHAR(100),
            Email VARCHAR(100),
            Contact_No VARCHAR(20),
            Specialization VARCHAR(50),
            Is_Available TINYINT(1) DEFAULT 1
        )
    """)
    # repair_request
    cur.execute("""
        CREATE TABLE IF NOT EXISTS repair_request(
            Request_ID VARCHAR(12) PRIMARY KEY,
            Resident_ID VARCHAR(8),
            Admin_ID VARCHAR(8),
            Personnel_ID VARCHAR(8),
            Req_Status VARCHAR(30),
            Issue_Description VARCHAR(500),
            Req_Date DATE,
            Completion_Date DATE,
            Created_At TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (Resident_ID) REFERENCES resident(Resident_ID),
            FOREIGN KEY (Admin_ID) REFERENCES society_admin(Admin_ID),
            FOREIGN KEY (Personnel_ID) REFERENCES repair_personnel(Personnel_ID)
        )
    """)
    conn.commit()
    cur.close()
    conn.close()

# ----------------- small DB operations used by UI -----------------
def verify_resident_login(rid, password):
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT Resident_ID, Resident_Name, password_hash FROM resident WHERE Resident_ID=%s", (rid,))
    r = cur.fetchone()
    cur.close(); conn.close()
    if not r: return None
    if r['password_hash'] == hash_password(password):
        return {'Resident_ID': r['Resident_ID'], 'Resident_Name': r['Resident_Name']}
    return None

def register_resident(resident_id, name, email, contact, block, flat, password):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            INSERT INTO resident (Resident_ID, Resident_Name, Email, Contact_No, Block_name, Flat_No, password_hash)
            VALUES (%s,%s,%s,%s,%s,%s,%s)
        """, (resident_id, name, email, contact, block, flat, hash_password(password)))
        conn.commit()
        return True, "Registered"
    except Error as e:
        return False, str(e)
    finally:
        cur.close(); conn.close()

def list_personnel():
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT Personnel_ID, Personnel_Name, Specialization, Contact_No, Is_Available FROM repair_personnel")
    rows = cur.fetchall()
    cur.close(); conn.close()
    return rows

def create_repair_request(request_id, resident_id, issue_description):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            INSERT INTO repair_request (Request_ID, Resident_ID, Req_Status, Issue_Description, Req_Date)
            VALUES (%s,%s,%s,%s,%s)
        """, (request_id, resident_id, 'Pending', issue_description, datetime.date.today()))
        conn.commit()
        return True, "Created"
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

# ----------------- UI -----------------
def gen_id(prefix='X', length=4):
    return prefix + ''.join(random.choices(string.digits, k=length))

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Society Repair Management")
        # full screen friendly: set large geometry but allow window managers
        self.state('zoomed')
        self.configure(bg='#f6f7fb')
        self.style = ttk.Style(self)
        self.style.theme_use('clam')

        # style tweaks
        self.style.configure('Title.TLabel', font=('Helvetica', 36, 'bold'), background='#f6f7fb')
        self.style.configure('Sub.TLabel', font=('Helvetica', 14), background='#f6f7fb')
        self.style.configure('Card.TFrame', background='white', relief='raised')
        self.style.configure('CardTitle.TLabel', font=('Helvetica', 20, 'bold'), background='white')
        self.style.configure('CardDesc.TLabel', font=('Helvetica', 12), background='white')
        self.style.configure('Primary.TButton', font=('Helvetica', 14, 'bold'), padding=10)
        self.style.configure('Secondary.TButton', font=('Helvetica', 12), padding=8)

        self._build_landing()

    def _build_landing(self):
        # main container
        main = ttk.Frame(self, padding=40, style='Card.TFrame', relief='flat', borderwidth=0)
        main.pack(fill='both', expand=True)

        # Title area
        title = ttk.Label(main, text="Welcome to Society\nRepair Management System", style='Title.TLabel', anchor='center', justify='center')
        title.pack(pady=(10,5))
        subtitle = ttk.Label(main, text="Streamline repair requests for your residential society", style='Sub.TLabel')
        subtitle.pack(pady=(0,30))

        # Cards container
        cards = ttk.Frame(main, style='Card.TFrame')
        cards.pack()

        # Resident Card
        resident_card = tk.Frame(cards, bg='white', bd=1, relief='raised', padx=30, pady=30)
        resident_card.grid(row=0, column=0, padx=30, pady=20, sticky='n')
        r_icon = ttk.Label(resident_card, text="👥", font=('Helvetica', 36), background='white')
        r_icon.pack()
        rtitle = ttk.Label(resident_card, text="Resident Login", style='CardTitle.TLabel', background='white')
        rtitle.pack(pady=(10,5))
        rdesc = ttk.Label(resident_card, text="Submit and track your repair requests", style='CardDesc.TLabel', background='white')
        rdesc.pack(pady=(0,15))
        ttk.Button(resident_card, text="Login as Resident", style='Primary.TButton', command=self.open_resident_login).pack(pady=6)
        ttk.Button(resident_card, text="Register", style='Secondary.TButton', command=self.open_resident_register).pack(pady=6)

        # Admin Card
        admin_card = tk.Frame(cards, bg='white', bd=1, relief='raised', padx=30, pady=30)
        admin_card.grid(row=0, column=1, padx=30, pady=20, sticky='n')
        atitle = ttk.Label(admin_card, text="Admin Login", style='CardTitle.TLabel', background='white')
        atitle.pack(pady=(10,5))
        adesc = ttk.Label(admin_card, text="Manage and track all repair requests", style='CardDesc.TLabel', background='white')
        adesc.pack(pady=(0,15))
        ttk.Button(admin_card, text="Login as Admin", style='Primary.TButton', command=self.open_admin_login).pack(pady=6)

    # ---------- Resident login + register ----------
    def open_resident_login(self):
        popup = tk.Toplevel(self)
        popup.title("Resident Login")
        popup.geometry("480x360")
        popup.transient(self)

        ttk.Label(popup, text="Resident Login", font=('Helvetica', 18, 'bold')).pack(pady=12)
        frm = ttk.Frame(popup, padding=10)
        frm.pack(fill='both', expand=True)

        ttk.Label(frm, text="Resident ID:").grid(row=0, column=0, sticky='e', pady=6)
        rid_entry = ttk.Entry(frm, width=30); rid_entry.grid(row=0, column=1, pady=6)

        ttk.Label(frm, text="Password:").grid(row=1, column=0, sticky='e', pady=6)
        pwd_entry = ttk.Entry(frm, width=30, show='*'); pwd_entry.grid(row=1, column=1, pady=6)

        def do_login():
            rid = rid_entry.get().strip()
            pw = pwd_entry.get()
            user = verify_resident_login(rid, pw)
            if user:
                popup.destroy()
                self.resident_dashboard(user)
            else:
                messagebox.showerror("Login failed", "Invalid credentials")

        ttk.Button(popup, text="Login", command=do_login, style='Primary.TButton').pack(pady=10)
        ttk.Button(popup, text="Close", command=popup.destroy).pack()

    def open_resident_register(self):
        popup = tk.Toplevel(self)
        popup.title("Resident Register")
        popup.geometry("520x520")
        popup.transient(self)

        ttk.Label(popup, text="Register as Resident", font=('Helvetica', 18, 'bold')).pack(pady=12)
        frm = ttk.Frame(popup, padding=10)
        frm.pack(fill='both', expand=True)

        labels = ["Resident ID", "Name", "Email", "Contact No", "Block", "Flat No", "Password"]
        entries = {}
        for i, lab in enumerate(labels):
            ttk.Label(frm, text=lab + ":").grid(row=i, column=0, sticky='e', pady=6)
            ent = ttk.Entry(frm, width=36, show='*' if lab == 'Password' else '')
            ent.grid(row=i, column=1, pady=6)
            entries[lab] = ent

        # prefill id
        entries["Resident ID"].insert(0, gen_id('RS',4))

        def submit():
            rid = entries["Resident ID"].get().strip()
            name = entries["Name"].get().strip()
            email = entries["Email"].get().strip()
            contact = entries["Contact No"].get().strip()
            block = entries["Block"].get().strip()
            flat = entries["Flat No"].get().strip()
            pwd = entries["Password"].get()
            if not (rid and name and pwd):
                messagebox.showerror("Error", "Provide Resident ID, name and password")
                return
            ok, msg = register_resident(rid, name, email, contact, block, flat, pwd)
            if ok:
                messagebox.showinfo("Done", f"Registered. Your Resident ID: {rid}")
                popup.destroy()
            else:
                messagebox.showerror("Error", msg)

        ttk.Button(popup, text="Register", command=submit, style='Primary.TButton').pack(pady=12)
        ttk.Button(popup, text="Close", command=popup.destroy).pack()

    # ---------- Resident Dashboard ----------
    def resident_dashboard(self, user):
        win = tk.Toplevel(self)
        win.title(f"Resident - {user['Resident_Name']}")
        win.state('zoomed')
        ttk.Label(win, text=f"Welcome, {user['Resident_Name']}", font=('Helvetica', 22, 'bold')).pack(pady=16)
        btnf = ttk.Frame(win); btnf.pack()
        ttk.Button(btnf, text="Raise Repair Request", style='Primary.TButton',
                   command=lambda: self._raise_request_popup(user['Resident_ID'])).grid(row=0, column=0, padx=10, pady=10)
        ttk.Button(btnf, text="View My Requests", style='Secondary.TButton',
                   command=lambda: self._view_requests_popup(user['Resident_ID'])).grid(row=0, column=1, padx=10, pady=10)
        ttk.Button(btnf, text="View Personnel", style='Secondary.TButton', command=self._view_personnel_popup).grid(row=0, column=2, padx=10, pady=10)

    def _raise_request_popup(self, resident_id):
        popup = tk.Toplevel(self)
        popup.title("Raise Request")
        popup.geometry("700x420")
        ttk.Label(popup, text="Describe Issue", font=('Helvetica', 14)).pack(pady=8)
        txt = tk.Text(popup, height=10, width=80); txt.pack(padx=12)
        def submit():
            desc = txt.get("1.0", 'end').strip()
            if not desc:
                messagebox.showerror("Error", "Enter description")
                return
            rid = "RQ" + datetime.datetime.now().strftime("%H%M%S")
            ok,msg = create_repair_request(rid, resident_id, desc)
            if ok:
                messagebox.showinfo("Created", f"Request {rid} created")
                popup.destroy()
            else:
                messagebox.showerror("Error", msg)
        ttk.Button(popup, text="Submit", command=submit, style='Primary.TButton').pack(pady=8)
        ttk.Button(popup, text="Close", command=popup.destroy).pack()

    def _view_requests_popup(self, resident_id):
        popup = tk.Toplevel(self); popup.title("My Requests"); popup.geometry("900x500")
        cols = ('Request_ID','Req_Status','Issue_Description','Req_Date','Completion_Date','Personnel_Name')
        tree = ttk.Treeview(popup, columns=cols, show='headings')
        for c in cols:
            tree.heading(c, text=c)
            tree.column(c, width=140)
        tree.pack(fill='both', expand=True)
        for r in get_requests_for_resident(resident_id):
            tree.insert('', 'end', values=(r['Request_ID'], r['Req_Status'], r['Issue_Description'][:80], str(r['Req_Date']), str(r.get('Completion_Date') or ''), r.get('Personnel_Name') or ''))
        ttk.Button(popup, text="Close", command=popup.destroy).pack(pady=6)

    def _view_personnel_popup(self):
        popup = tk.Toplevel(self); popup.title("Personnel"); popup.geometry("800x450")
        cols = ('Personnel_ID','Personnel_Name','Specialization','Contact_No','Is_Available')
        tree = ttk.Treeview(popup, columns=cols, show='headings')
        for c in cols:
            tree.heading(c, text=c)
            tree.column(c, width=140)
        tree.pack(fill='both', expand=True)
        for r in list_personnel():
            tree.insert('', 'end', values=(r['Personnel_ID'], r['Personnel_Name'], r['Specialization'], r['Contact_No'], 'Yes' if r['Is_Available'] else 'No'))
        ttk.Button(popup, text="Close", command=popup.destroy).pack(pady=6)

    # ---------- Admin login ----------
    def open_admin_login(self):
        popup = tk.Toplevel(self)
        popup.title("Admin Login")
        popup.geometry("460x300")
        popup.transient(self)
        ttk.Label(popup, text="Admin Login", font=('Helvetica', 18, 'bold')).pack(pady=12)
        frm = ttk.Frame(popup, padding=10)
        frm.pack()

        ttk.Label(frm, text="Admin ID:").grid(row=0, column=0, pady=6)
        aid = ttk.Entry(frm)
        aid.grid(row=0, column=1, pady=6)

        ttk.Label(frm, text="Password:").grid(row=1, column=0, pady=6)
        pwd = ttk.Entry(frm, show='*')
        pwd.grid(row=1, column=1, pady=6)

        def do_login():
            conn = get_connection()
            cur = conn.cursor(dictionary=True)
            cur.execute("SELECT Admin_ID, Admin_Name, password_hash FROM society_admin WHERE Admin_ID=%s", (aid.get(),))
            r = cur.fetchone()
            cur.close()
            conn.close()

            if r and r['password_hash'] == hash_password(pwd.get()):
                popup.destroy()
                messagebox.showinfo("Admin", f"Welcome, {r['Admin_Name']}")
                self.withdraw()  # hide main window while admin UI is active

                # ✅ Open admin UI frame
                admin_window = tk.Toplevel(self)
                admin_window.title(f"Admin Dashboard - {r['Admin_Name']}")
                admin_window.geometry("1200x700")
                frame = AdminFrame(admin_window, app=self)

                # Restore main window when admin closes
                admin_window.protocol("WM_DELETE_WINDOW", lambda: (admin_window.destroy(), self.deiconify()))
            else:
                messagebox.showerror("Login failed", "Invalid credentials")

        ttk.Button(popup, text="Login", command=do_login, style='Primary.TButton').pack(pady=8)
        ttk.Button(popup, text="Close", command=popup.destroy).pack()


# ----------------- run -----------------
if __name__ == '__main__':
    try:
        initialize_database()
    except Error as e:
        # Provide friendly message and stop if DB credentials invalid
        messagebox.showerror("Database error", f"Could not initialize database.\n\nMySQL Error: {e}")
        raise SystemExit(1)

    app = App()
    app.mainloop()
