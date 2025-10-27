# 🏢 Society Repair Management System

A GUI-based **Society Repair Management System** built using **Python (Tkinter)** and **MySQL** for efficient handling of residential maintenance requests, personnel assignment, and admin management.

---

## 🧩 Overview

This project is designed to digitalize and streamline how a residential society manages repair requests raised by residents and handled by repair personnel.  
It provides two primary roles:

- 👤 **Residents:** Can log in, submit maintenance/repair requests, and check request status.
- 🧑‍💼 **Admin:** Can manage repair personnel, assign them to requests, and update repair statuses.

---

## 🛠️ Tech Stack

| Component | Technology |
|------------|-------------|
| Frontend GUI | Tkinter (Python) |
| Backend | Python 3.x |
| Database | MySQL |
| Styling | Tkinter Themes (Blue/Gray for Residents, Lime/Gray for Admin) |
| Password Security | SHA256 Hashing |

---

## ⚙️ Features

### 🧑‍💻 Resident Module
- Register and log in securely (password stored as hash)
- Submit repair requests
- View request history and current status
- See available repair personnel and their specialization

### 🧑‍💼 Admin Module
- Secure admin login
- Manage and add repair personnel
- View all repair requests (pending, in-progress, completed)
- Assign personnel to specific repair requests
- Update request statuses
- Toggle personnel availability

### 🔐 Security
- Passwords stored as **SHA256 hashes** (no plain-text passwords)
- Login verification handled with hashed comparison

---


---

## 💾 Database Schema

### Tables Used
1. **`society_admin`**
   - `Admin_ID`, `Admin_Name`, `password_hash`

2. **`resident`**
   - `Resident_ID`, `Name`, `Block`, `Flat_No`, `Email`, `password_hash`

3. **`repair_personnel`**
   - `Personnel_ID`, `Personnel_Name`, `Email`, `Contact_No`, `Specialization`, `Is_Available`

4. **`repair_request`**
   - `Request_ID`, `Resident_ID`, `Personnel_ID`, `Issue_Description`, `Req_Status`, `Req_Date`, `Completion_Date`

## HOW TO RUN

Prerequisites

Install Python 3.10+

Install MySQL Server

Create a database (e.g., society_db)

Update connection details in db.py

python main.py

## MySQL sample data
load sample data from sample_data.sql
Tables and Database are created from code , if not found while running . 
