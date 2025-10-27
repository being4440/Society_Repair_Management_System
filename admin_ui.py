# admin_ui.py
import tkinter as tk
from tkinter import ttk, messagebox
from db import verify_admin_login, list_personnel, add_personnel, get_all_requests, assign_personnel_to_request, update_request_status, set_personnel_availability
import random, string

def gen_id(prefix='P', length=3):
    return f"{prefix}{''.join(random.choices(string.digits, k=length))}"

class AdminFrame(ttk.Frame):
    def __init__(self, parent, app, admin_name=None, admin_id=None):
        super().__init__(parent)
        self.app = app
        self.admin_name = admin_name
        self.admin_id = admin_id

        # color theme
        self.configure(style="Admin.TFrame")
        style = ttk.Style(self)
        style.configure("Admin.TFrame", background="#808080")  # gray background
        style.configure("AdminTitle.TLabel", font=("Helvetica", 22, "bold"), background="#808080", foreground="#00FF00")
        style.configure("AdminButton.TButton", font=("Helvetica", 12, "bold"), padding=8)

        self.pack(fill='both', expand=True)
        self.create_widgets()

    def create_widgets(self):
        """Main admin dashboard"""
        header = ttk.Label(
            self,
            text=f"Admin Dashboard - {self.admin_name or ''}",
            style="AdminTitle.TLabel"
        )
        header.pack(pady=15)

        btnf = ttk.Frame(self, padding=10)
        btnf.pack(pady=8)

        ttk.Button(btnf, text="View Requests", style="AdminButton.TButton", command=self.show_requests).grid(row=0, column=0, padx=8)
        ttk.Button(btnf, text="Manage Personnel", style="AdminButton.TButton", command=self.show_personnel).grid(row=0, column=1, padx=8)
        ttk.Button(btnf, text="Logout", style="AdminButton.TButton", command=self.logout).grid(row=0, column=2, padx=8)

    def logout(self):
        self.master.destroy()
        self.app.deiconify()

    # ---------- Personnel Management ----------
    def show_personnel(self):
        popup = tk.Toplevel(self)
        popup.title("Manage Personnel")
        popup.geometry("800x450")

        topf = ttk.Frame(popup)
        topf.pack(fill='x', pady=6)

        ttk.Label(topf, text="Add Personnel").grid(row=0, column=0, padx=6)
        pid = gen_id('P', 3)
        self.add_pid = ttk.Entry(topf)
        self.add_pid.grid(row=0, column=1)
        self.add_pid.insert(0, pid)

        ttk.Label(topf, text="Name").grid(row=0, column=2)
        self.add_name = ttk.Entry(topf)
        self.add_name.grid(row=0, column=3)

        ttk.Label(topf, text="Email").grid(row=0, column=4)
        self.add_email = ttk.Entry(topf)
        self.add_email.grid(row=0, column=5)

        ttk.Label(topf, text="Contact").grid(row=1, column=0)
        self.add_contact = ttk.Entry(topf)
        self.add_contact.grid(row=1, column=1)

        ttk.Label(topf, text="Specialization").grid(row=1, column=2)
        self.add_spec = ttk.Entry(topf)
        self.add_spec.grid(row=1, column=3)

        ttk.Button(topf, text="Add", command=self.handle_add_personnel).grid(row=1, column=5)

        cols = ('Personnel_ID', 'Personnel_Name', 'Specialization', 'Contact_No', 'Is_Available')
        tree = ttk.Treeview(popup, columns=cols, show='headings')
        for c in cols:
            tree.heading(c, text=c)
            tree.column(c, width=130)
        tree.pack(fill='both', expand=True)

        rows = list_personnel()
        for r in rows:
            tree.insert(
                '',
                'end',
                values=(
                    r['Personnel_ID'],
                    r['Personnel_Name'],
                    r['Specialization'],
                    r['Contact_No'],
                    'Yes' if r['Is_Available'] else 'No'
                )
            )

    def handle_add_personnel(self):
        pid = self.add_pid.get().strip()
        name = self.add_name.get().strip()
        email = self.add_email.get().strip()
        contact = self.add_contact.get().strip()
        spec = self.add_spec.get().strip()
        ok, msg = add_personnel(pid, name, email, contact, spec)
        if ok:
            messagebox.showinfo("Success", "Personnel added")
        else:
            messagebox.showerror("Error", msg)

    # ---------- Request Management ----------
    def show_requests(self):
        popup = tk.Toplevel(self)
        popup.title("All Requests")
        popup.geometry("1000x500")

        cols = (
            'Request_ID', 'Resident_ID', 'Resident_Name', 'Personnel_ID', 'Personnel_Name',
            'Req_Status', 'Issue_Description', 'Req_Date', 'Completion_Date'
        )
        tree = ttk.Treeview(popup, columns=cols, show='headings')
        for c in cols:
            tree.heading(c, text=c)
            tree.column(c, width=110)
        tree.pack(fill='both', expand=True)

        rows = get_all_requests()
        for r in rows:
            tree.insert(
                '',
                'end',
                values=(
                    r['Request_ID'], r['Resident_ID'], r.get('Resident_Name') or '',
                    r.get('Personnel_ID') or '', r.get('Personnel_Name') or '',
                    r['Req_Status'], r['Issue_Description'][:40],
                    str(r['Req_Date']), str(r.get('Completion_Date') or '')
                )
            )

        ctrl = ttk.Frame(popup)
        ctrl.pack(fill='x', pady=6)
        ttk.Label(ctrl, text="Request ID:").grid(row=0, column=0)
        self.req_id_entry = ttk.Entry(ctrl)
        self.req_id_entry.grid(row=0, column=1)
        ttk.Label(ctrl, text="Personnel ID:").grid(row=0, column=2)
        self.assign_pid = ttk.Entry(ctrl)
        self.assign_pid.grid(row=0, column=3)
        ttk.Button(ctrl, text="Assign", command=self.handle_assign).grid(row=0, column=4, padx=6)
        ttk.Label(ctrl, text="Set Status (e.g., In Progress, Completed):").grid(row=1, column=0, columnspan=2)
        self.status_entry = ttk.Entry(ctrl)
        self.status_entry.grid(row=1, column=2)
        ttk.Button(ctrl, text="Update Status", command=self.handle_update_status).grid(row=1, column=3)

    def handle_assign(self):
        rid = self.req_id_entry.get().strip()
        pid = self.assign_pid.get().strip()
        if not (rid and pid):
            messagebox.showerror("Error", "Provide both Request ID and Personnel ID")
            return
        ok, msg = assign_personnel_to_request(rid, pid)
        if ok:
            messagebox.showinfo("Assigned", "Personnel assigned")
        else:
            messagebox.showerror("Error", msg)

    def handle_update_status(self):
        rid = self.req_id_entry.get().strip()
        status = self.status_entry.get().strip()
        if not (rid and status):
            messagebox.showerror("Error", "Provide Request ID and status")
            return
        ok, msg = update_request_status(rid, status)
        if ok:
            messagebox.showinfo("Updated", msg)
        else:
            messagebox.showerror("Error", msg)