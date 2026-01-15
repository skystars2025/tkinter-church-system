import tkinter as tk
from tkinter import messagebox
import sqlite3
from datetime import datetime

# ---------------- DB SETUP ----------------
conn = sqlite3.connect("database.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS members (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS contributions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    member_id INTEGER,
    month TEXT,
    year INTEGER,
    attendance REAL,
    society REAL,
    uwaka REAL,
    wawata REAL,
    construction REAL
)
""")
conn.commit()

# ---------------- FUNCTIONS ----------------
def add_member():
    name = member_entry.get()
    if not name:
        return

    try:
        cursor.execute("INSERT INTO members (name) VALUES (?)", (name,))
        conn.commit()
        member_entry.delete(0, tk.END)
        load_members()
    except:
        messagebox.showerror("Error", "Member already exists")

def load_members():
    member_list.delete(0, tk.END)
    cursor.execute("SELECT name FROM members")
    for row in cursor.fetchall():
        member_list.insert(tk.END, row[0])

def save_contribution():
    selected = member_list.curselection()
    if not selected:
        return

    name = member_list.get(selected)
    cursor.execute("SELECT id FROM members WHERE name=?", (name,))
    member_id = cursor.fetchone()[0]

    month = datetime.now().strftime("%B")
    year = datetime.now().year

    data = (
        member_id,
        month,
        year,
        float(attendance.get()),
        float(society.get()),
        float(uwaka.get()),
        float(wawata.get()),
        float(construction.get())
    )

    cursor.execute("""
    INSERT INTO contributions 
    (member_id, month, year, attendance, society, uwaka, wawata, construction)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, data)

    conn.commit()
    messagebox.showinfo("Saved", "Contribution recorded")

def show_year_total():
    selected = member_list.curselection()
    if not selected:
        return

    name = member_list.get(selected)
    cursor.execute("SELECT id FROM members WHERE name=?", (name,))
    member_id = cursor.fetchone()[0]

    cursor.execute("""
    SELECT 
    SUM(attendance + society + uwaka + wawata + construction)
    FROM contributions
    WHERE member_id=? AND year=?
    """, (member_id, datetime.now().year))

    total = cursor.fetchone()[0] or 0
    messagebox.showinfo("Year Total", f"{name}\nTotal: {total:.2f}")

# ---------------- UI ----------------
root = tk.Tk()
root.title("Church Contribution System")
root.geometry("600x400")

tk.Label(root, text="Add Member").pack()
member_entry = tk.Entry(root)
member_entry.pack()
tk.Button(root, text="Add", command=add_member).pack()

tk.Label(root, text="Members").pack()
member_list = tk.Listbox(root)
member_list.pack(fill=tk.X)

tk.Label(root, text="Contributions").pack()

attendance = tk.Entry(root)
society = tk.Entry(root)
uwaka = tk.Entry(root)
wawata = tk.Entry(root)
construction = tk.Entry(root)

for label, field in [
    ("Attendance", attendance),
    ("Society", society),
    ("Uwaka", uwaka),
    ("Wawata", wawata),
    ("Construction", construction)
]:
    tk.Label(root, text=label).pack()
    field.pack()

tk.Button(root, text="Save Contribution", command=save_contribution).pack(pady=5)
tk.Button(root, text="View Year Total", command=show_year_total).pack()

load_members()
root.mainloop()
