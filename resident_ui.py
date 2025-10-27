# resident_ui.py
import tkinter as tk
from tkinter import ttk, messagebox
from db import register_resident, verify_resident_login, create_repair_request, get_requests_for_resident, list_personnel
import random
import string

def gen_id(prefix='R', length=3):
    return f"{prefix}{''.join(random.choices(string.digits, k=length))}"

class ResidentFrame(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.pack(fill='both', expand=True)
        self.create_widgets()

    def create_widgets(self):
        self.login_frame = ttk.Frame(self)
        self.reg_frame = ttk.Frame(self)
        self.main_frame = ttk.Frame(self)

        # --- Login frame ---
        ttk.Label(self.login_frame, text="Resident Login", font=('Arial', 20)).pack(pady=10)
        lf = ttk.Frame(self.login_frame); lf.pack()
        ttk.Label(lf, text="Resident ID:").grid(row=0, column=0, sticky='e')
        self.login_resident_id = ttk.Entry(lf); self.login_resident_id.grid(row=0, column=1)
        ttk.Label(lf, text="Password:").grid(row=1, column=0, sticky='e')
        self.login_password = ttk.Entry(lf, show='*'); self.login_password.grid(row=1, column=1)
        ttk.Button(self.login_frame, text="Login", command=self.handle_login).pack(pady=6)
        ttk.Button(self.login_frame, text="Register", command=self.show_register).pack()

        # --- Register frame ---
        ttk.Label(self.reg_frame, text="Resident Registration", font=('Arial', 20)).pack(pady=10)
        rf = ttk.Frame(self.reg_frame); rf.pack()
        self.reg_resident_id = ttk.Entry(rf); ttk.Label(rf, text="Resident ID:").grid(row=0,column=0); self.reg_resident_id.grid(row=0,column=1)
        self.reg_name = ttk.Entry(rf); ttk.Label(rf, text="Name:").grid(row=1,column=0); self.reg_name.grid(row=1,column=1)
        self.reg_email = ttk.Entry(rf); ttk.Label(rf, text="Email:").grid(row=2,column=0); self.reg_email.grid(row=2,column=1)
        self.reg_contact = ttk.Entry(rf); ttk.Label(rf, text="Contact No:").grid(row=3,column=0); self.reg_contact.grid(row=3,column=1)
        self.reg_block = ttk.Entry(rf); ttk.Label(rf, text="Block:").grid(row=4,column=0); self.reg_block.grid(row=4,column=1)
        self.reg_flat = ttk.Entry(rf); ttk.Label(rf, text="Flat No:").grid(row=5,column=0); self.reg_flat.grid(row=5,column=1)
        self.reg_password = ttk.Entry(rf, show='*'); ttk.Label(rf, text="Password:").grid(row=6,column=0); self.reg_password.grid(row=6,column=1)
        ttk.Button(self.reg_frame, text="Submit", command=self.handle_register).pack(pady=8)
        ttk.Button(self.reg_frame, text="Back to Login", command=self.show_login).pack()

        # --- Main frame after login ---
        ttk.Label(self.main_frame, text="Resident Dashboard", font=('Arial', 20)).pack(pady=8)
        btnf = ttk.Frame(self.main_frame); btnf.pack(pady=6)
        ttk.Button(btnf, text="Raise Repair Request", command=self.show_raise).grid(row=0,column=0,padx=8)
        ttk.Button(btnf, text="View My Requests", command=self.show_history).grid(row=0,column=1,padx=8)
        ttk.Button(btnf, text="View Personnel", command=self.show_personnel).grid(row=0,column=2,padx=8)
        ttk.Button(btnf, text="Logout", command=self.logout).grid(row=0,column=3,padx=8)

        self.show_login()

    def clear_frames(self):
        for f in (self.login_frame, self.reg_frame, self.main_frame):
            f.pack_forget()

    def show_login(self):
        self.clear_frames()
        self.login_frame.pack(fill='both', expand=True)

    def show_register(self):
        self.clear_frames()
        # prefill id
        self.reg_resident_id.delete(0, 'end')
        self.reg_resident_id.insert(0, gen_id('RS',3))
        self.reg_frame.pack(fill='both', expand=True)

    def handle_register(self):
        rid = self.reg_resident_id.get().strip()
        name = self.reg_name.get().strip()
        email = self.reg_email.get().strip()
        contact = self.reg_contact.get().strip()
        block = self.reg_block.get().strip()
        flat = self.reg_flat.get().strip()
        pwd = self.reg_password.get()
        if not (rid and name and pwd):
            messagebox.showerror("Error", "Please provide at least ID, name and password")
            return
        ok, msg = register_resident(rid, name, email, contact, block, flat, pwd)
        if ok:
            messagebox.showinfo("Success", f"Registered. Your Resident ID: {rid}")
            self.show_login()
        else:
            messagebox.showerror("Error", msg)

    def handle_login(self):
        rid = self.login_resident_id.get().strip()
        pwd = self.login_password.get()
        user = verify_resident_login(rid, pwd)
        if user:
            self.current_user = user
            self.show_main()
        else:
            messagebox.showerror("Login failed", "Invalid credentials")

    # Main dashboard / small modals:
    def show_main(self):
        self.clear_frames()
        self.main_frame.pack(fill='both', expand=True)

    def logout(self):
        self.current_user = None
        self.show_login()

    def show_raise(self):
        popup = tk.Toplevel(self)
        popup.title("Raise Repair Request")
        popup.geometry("500x300")
        ttk.Label(popup, text="Issue Description:").pack(pady=6)
        txt = tk.Text(popup, height=6, width=60)
        txt.pack()
        def submit():
            desc = txt.get("1.0","end").strip()
            if not desc:
                messagebox.showerror("Error", "Please enter description")
                return
            # generate ID
            rid = gen_id('Q',3)
            ok,msg = create_repair_request(rid, self.current_user['Resident_ID'], desc)
            if ok:
                messagebox.showinfo("Success", f"Request raised with ID {rid}")
                popup.destroy()
            else:
                messagebox.showerror("Error", msg)
        ttk.Button(popup, text="Submit", command=submit).pack(pady=8)

    def show_history(self):
        rows = get_requests_for_resident(self.current_user['Resident_ID'])
        popup = tk.Toplevel(self)
        popup.title("My Requests")
        popup.geometry("800x400")
        cols = ('Request_ID','Req_Status','Issue_Description','Req_Date','Completion_Date','Personnel_Name')
        tree = ttk.Treeview(popup, columns=cols, show='headings')
        for c in cols:
            tree.heading(c, text=c)
            tree.column(c, width=120)
        tree.pack(fill='both', expand=True)
        for r in rows:
            tree.insert('', 'end', values=(r['Request_ID'], r['Req_Status'], r['Issue_Description'][:40], str(r['Req_Date']), str(r.get('Completion_Date') or ''), r.get('Personnel_Name') or ''))
    
    def show_personnel(self):
        rows = list_personnel()
        popup = tk.Toplevel(self)
        popup.title("Repair Personnel")
        popup.geometry("700x400")
        cols = ('Personnel_ID','Personnel_Name','Specialization','Contact_No','Is_Available')
        tree = ttk.Treeview(popup, columns=cols, show='headings')
        for c in cols:
            tree.heading(c, text=c)
            tree.column(c, width=130)
        tree.pack(fill='both', expand=True)
        for r in rows:
            tree.insert('', 'end', values=(r['Personnel_ID'], r['Personnel_Name'], r['Specialization'], r['Contact_No'], 'Yes' if r['Is_Available'] else 'No'))
