import tkinter as tk
from tkinter import messagebox, ttk, filedialog
import sqlite3
from datetime import datetime
from openpyxl import Workbook

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
def load_members():
    member_list.delete(0, tk.END)
    cursor.execute("SELECT name FROM members ORDER BY name")
    for row in cursor.fetchall():
        member_list.insert(tk.END, row[0])

def add_member():
    name = member_entry.get().strip()
    if not name:
        return
    try:
        cursor.execute("INSERT INTO members (name) VALUES (?)", (name,))
        conn.commit()
        member_entry.delete(0, tk.END)
        load_members()
    except:
        messagebox.showerror("Error", "Member already exists")

def save_contribution():
    if not member_list.curselection():
        messagebox.showwarning("Select member", "Select a member first")
        return

    try:
        values = [
            float(attendance.get() or 0),
            float(society.get() or 0),
            float(uwaka.get() or 0),
            float(wawata.get() or 0),
            float(construction.get() or 0)
        ]
    except:
        messagebox.showerror("Error", "Enter valid numbers")
        return

    name = member_list.get(member_list.curselection())
    cursor.execute("SELECT id FROM members WHERE name=?", (name,))
    member_id = cursor.fetchone()[0]

    cursor.execute("""
    INSERT INTO contributions
    (member_id, month, year, attendance, society, uwaka, wawata, construction)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (member_id, datetime.now().strftime("%B"), datetime.now().year, *values))

    conn.commit()
    messagebox.showinfo("Saved", "Contribution saved")

def view_member_details():
    if not member_list.curselection():
        return

    name = member_list.get(member_list.curselection())
    cursor.execute("SELECT id FROM members WHERE name=?", (name,))
    member_id = cursor.fetchone()[0]

    win = tk.Toplevel(root)
    win.title(f"{name} - Contributions")
    win.geometry("800x400")

    tree = ttk.Treeview(win, columns=("Month","Att","Soc","Uwaka","Wawata","Cons","Total"), show="headings")
    for col in tree["columns"]:
        tree.heading(col, text=col)
        tree.column(col, width=100)
    tree.pack(fill=tk.BOTH, expand=True)

    cursor.execute("""
    SELECT month, attendance, society, uwaka, wawata, construction,
    attendance+society+uwaka+wawata+construction
    FROM contributions WHERE member_id=?
    """, (member_id,))

    year_total = 0
    for row in cursor.fetchall():
        tree.insert("", tk.END, values=row)
        year_total += row[-1]

    tk.Label(win, text=f"YEAR TOTAL: {year_total:.2f}", font=("Arial", 12, "bold")).pack(pady=5)

def export_selected_member():
    if not member_list.curselection():
        return

    name = member_list.get(member_list.curselection())
    cursor.execute("SELECT id FROM members WHERE name=?", (name,))
    member_id = cursor.fetchone()[0]

    wb = Workbook()
    ws = wb.active
    ws.append(["Month","Attendance","Society","Uwaka","Wawata","Construction","Total"])

    cursor.execute("""
    SELECT month, attendance, society, uwaka, wawata, construction,
    attendance+society+uwaka+wawata+construction
    FROM contributions WHERE member_id=?
    """, (member_id,))

    for row in cursor.fetchall():
        ws.append(row)

    file = filedialog.asksaveasfilename(defaultextension=".xlsx", initialfile=f"{name}.xlsx")
    if file:
        wb.save(file)
        messagebox.showinfo("Exported", "Excel file created")

def export_all_members():
    wb = Workbook()
    ws = wb.active
    ws.append(["Member","Month","Attendance","Society","Uwaka","Wawata","Construction","Total"])

    cursor.execute("""
    SELECT m.name, c.month, c.attendance, c.society, c.uwaka, c.wawata, c.construction,
    c.attendance+c.society+c.uwaka+c.wawata+c.construction
    FROM contributions c
    JOIN members m ON m.id = c.member_id
    """)

    for row in cursor.fetchall():
        ws.append(row)

    file = filedialog.asksaveasfilename(defaultextension=".xlsx", initialfile="All_Members.xlsx")
    if file:
        wb.save(file)
        messagebox.showinfo("Exported", "Excel file created")

# ---------------- UI ----------------
root = tk.Tk()
root.title("Advanced Church Contribution System")
root.geometry("900x600")

tk.Label(root, text="Add Member").pack()
member_entry = tk.Entry(root)
member_entry.pack()
tk.Button(root, text="Add Member", command=add_member).pack(pady=5)

member_list = tk.Listbox(root, height=8)
member_list.pack(fill=tk.X, padx=10)

btn_frame = tk.Frame(root)
btn_frame.pack()

tk.Button(btn_frame, text="View Details", command=view_member_details).grid(row=0, column=0, padx=5)
tk.Button(btn_frame, text="Export Member Excel", command=export_selected_member).grid(row=0, column=1, padx=5)
tk.Button(btn_frame, text="Export ALL Excel", command=export_all_members).grid(row=0, column=2, padx=5)

tk.Label(root, text="Add Contribution").pack(pady=10)

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

tk.Button(root, text="Save Contribution", command=save_contribution).pack(pady=10)

load_members()
root.mainloop()
