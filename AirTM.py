import mysql.connector
import tkinter as tk
from tkinter import simpledialog, messagebox, ttk, font
from PIL import Image, ImageTk
import os

# DB Connection
db = mysql.connector.connect(
    host="localhost", user="root", passwd="Abhay@123", database="new", charset="utf8"
)
cur = db.cursor()

OWN_PH = "9876543210"
OWN_DOB = "1990-01-01"
pwd = "ANANYA"

KM_FEE = 10
KG_FEE = 100

# Colors
PRIM = "#1E3D59"  # Dark blue
SEC = "#F5F0E1"   # Off-white
ACC = "#FF6E40"   # Orange
LITE = "#FDFCFB"  # White
TXT = "#333333"   # Dark gray

# Main Window
root = tk.Tk()
root.title("AIRBIPES Tickets")
root.geometry("800x600")
root.configure(bg=SEC)

# Fonts
ttl_f = font.Font(family="Helvetica", size=18, weight="bold")
sub_f = font.Font(family="Helvetica", size=14, weight="bold")
btn_f = font.Font(family="Helvetica", size=12)
lbl_f = font.Font(family="Helvetica", size=11)

# Styles
stl = ttk.Style()
stl.theme_use('clam')
stl.configure('TFrame', background=SEC)
stl.configure('TButton', 
               background=PRIM,
               foreground=LITE,
               font=btn_f,
               padding=10)
stl.map('TButton', 
         background=[('active', ACC), ('pressed', PRIM)])
stl.configure('TLabel', 
               background=SEC,
               foreground=TXT,
               font=lbl_f)
stl.configure('TEntry', 
               font=lbl_f, 
               padding=5)

# Header
hdr = ttk.Frame(root, style='TFrame')
hdr.pack(fill=tk.X, padx=20, pady=20)

hdr_lbl = tk.Label(hdr, 
                       text="Air Ticket System", 
                       font=ttl_f, 
                       bg=SEC, 
                       fg=PRIM)
hdr_lbl.pack(pady=10)

# Button frame
btn_frm = ttk.Frame(root, style='TFrame')
btn_frm.pack(pady=20)

# Make styled button
def mk_btn(par, txt, cmd):
    btn = ttk.Button(par, text=txt, command=cmd, style='TButton')
    btn.pack(fill=tk.X, padx=50, pady=8)
    return btn

# Make form field
def mk_fld(par, txt):
    frm = ttk.Frame(par, style='TFrame')
    frm.pack(fill=tk.X, padx=20, pady=5)
    
    lbl = ttk.Label(frm, text=txt, style='TLabel', width=25)
    lbl.pack(side=tk.LEFT, padx=5)
    
    ent = ttk.Entry(frm, style='TEntry')
    ent.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
    
    return ent

# Make form window
def mk_win(ttl, wid=400, hgt=500):
    win = tk.Toplevel(root)
    win.title(ttl)
    win.geometry(f"{wid}x{hgt}")
    win.configure(bg=SEC)
    
    # Header
    hdr = tk.Label(win, text=ttl, font=sub_f, bg=SEC, fg=PRIM)
    hdr.pack(pady=15)
    
    # Content frame
    cnt = ttk.Frame(win, style='TFrame')
    cnt.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
    
    return win, cnt

# Register Customer
def reg():
    win, cnt = mk_win("Register Customer")
    
    cid = mk_fld(cnt, "ID")
    nam = mk_fld(cnt, "Name")
    adr = mk_fld(cnt, "Address")
    dat = mk_fld(cnt, "Date (YYYY-MM-DD)")
    src = mk_fld(cnt, "From")
    dst = mk_fld(cnt, "To")
    
    def sub():
        try:
            sql = 'INSERT INTO pdata (custno, custname, addr, jrdate, source, destination) VALUES (%s, %s, %s, %s, %s, %s)'
            cur.execute(sql, (int(cid.get()), nam.get(), adr.get(), dat.get(), src.get(), dst.get()))
            db.commit()
            messagebox.showinfo("Done", "Customer Added!")
            win.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Bad Data! {str(e)}")
    
    btn_frm = ttk.Frame(cnt, style='TFrame')
    btn_frm.pack(pady=20)
    
    sub_btn = ttk.Button(btn_frm, text="Add", command=sub, style='TButton')
    sub_btn.pack(pady=10)

# Book Ticket
def book():
    win, cnt = mk_win("Book Ticket")
    
    cid = mk_fld(cnt, "ID")
    cls = mk_fld(cnt, "Class (1,2,3)")
    ppl = mk_fld(cnt, "People")
    kg = mk_fld(cnt, "Bags (kg)")
    km = mk_fld(cnt, "Distance (km)")
    
    def sub():
        cost = {1: 6000, 2: 4000, 3: 2000}
        try:
            cur.execute("SELECT * FROM pdata WHERE custno = %s", (int(cid.get()),))
            if cur.fetchone() is None:
                messagebox.showerror("Error", "No ID! Register First!")
                return

            cls_v = int(cls.get())
            if cls_v not in cost:
                messagebox.showerror("Error", "Bad Class!")
                return

            tkt = cost[cls_v] * int(ppl.get())
            km_c = KM_FEE * int(km.get())
            lug = KG_FEE * int(kg.get())
            tot = tkt + km_c + lug

            sql = "INSERT INTO tkt (custno, tkt_tot, lug_tot, g_tot) VALUES (%s, %s, %s, %s)"
            cur.execute(sql, (int(cid.get()), tkt, lug, tot))
            db.commit()

            messagebox.showinfo("Done", f"Cost: {tot}")
            win.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Bad Data! {str(e)}")
    
    btn_frm = ttk.Frame(cnt, style='TFrame')
    btn_frm.pack(pady=20)
    
    sub_btn = ttk.Button(btn_frm, text="Book", command=sub, style='TButton')
    sub_btn.pack(pady=10)

# Show Bill
def bill():
    win, cnt = mk_win("Show Bill", wid=400, hgt=300)
    
    cid = mk_fld(cnt, "ID")
    
    def sub():
        try:
            cur.execute("SELECT pdata.custno, pdata.custname, pdata.addr, pdata.source, pdata.destination, tkt.tkt_tot, tkt.lug_tot, g_tot FROM pdata INNER JOIN tkt ON pdata.custno = tkt.custno WHERE pdata.custno = %s", (int(cid.get()),))
            res = cur.fetchone()

            if res:
                # Show bill info
                bil = ttk.Frame(cnt, style='TFrame')
                bil.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
                
                # Format bill
                inf = [
                    f"Name: {res[1]}",
                    f"From: {res[3]} To: {res[4]}",
                    f"Tkt: ₹{res[5]}",
                    f"Bag: ₹{res[6]}",
                    f"Total: ₹{res[7]}"
                ]
                
                for i in inf:
                    l = ttk.Label(bil, text=i, style='TLabel')
                    l.pack(anchor=tk.W, pady=2)
            else:
                messagebox.showerror("Error", "No Data!")
        except Exception as e:
            messagebox.showerror("Error", f"Bad ID! {str(e)}")
    
    btn_frm = ttk.Frame(cnt, style='TFrame')
    btn_frm.pack(pady=20)
    
    sub_btn = ttk.Button(btn_frm, text="Show", command=sub, style='TButton')
    sub_btn.pack(pady=10)

# Show All Customers
def all():
    pw = tk.simpledialog.askstring("Login", "Password:", show='*')
    if pw == pwd:
        try:
            cur.execute("SELECT * FROM pdata")
            res = cur.fetchall()
            
            if res:
                # New window for records
                win = tk.Toplevel(root)
                win.title("All Customers")
                win.geometry("600x400")
                win.configure(bg=SEC)
                
                # Title
                ttl = tk.Label(win, text="Customers", 
                                      font=sub_f, bg=SEC, fg=PRIM)
                ttl.pack(pady=10)
                
                # Create Table
                cols = ("ID", "Name", "Address", "Date", "From", "To")
                tree = ttk.Treeview(win, columns=cols, show="headings")
                
                # Column setup
                for col in cols:
                    tree.heading(col, text=col)
                    tree.column(col, width=80, anchor="center")
                
                # Add data
                for row in res:
                    tree.insert("", tk.END, values=row)
                
                # Scrollbar
                scrl = ttk.Scrollbar(win, orient=tk.VERTICAL, command=tree.yview)
                tree.configure(yscroll=scrl.set)
                scrl.pack(side=tk.RIGHT, fill=tk.Y)
                tree.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
                
                # Close button
                cls_btn = ttk.Button(win, text="Close", 
                                      command=win.destroy, style='TButton')
                cls_btn.pack(pady=10)
            else:
                messagebox.showinfo("Empty", "No data.")
        except Exception as e:
            messagebox.showerror("Error", f"Can't load: {str(e)}")
    else:
        messagebox.showerror("Denied", "Wrong Password!")

# Delete records
def dele():
    pw = tk.simpledialog.askstring("Login", "Password:", show='*')
    if pw == pwd:
        win, cnt = mk_win("Delete Customer", wid=400, hgt=250)
        
        cid = mk_fld(cnt, "ID to Delete")
        
        def sub():
            try:
                id = int(cid.get())
                # Confirm
                ok = messagebox.askyesno("Sure?", 
                                            f"Delete ID {id}?")
                if ok:
                    # Delete ticket first
                    cur.execute("DELETE FROM tkt WHERE custno = %s", (id,))
                    # Then delete customer
                    cur.execute("DELETE FROM pdata WHERE custno = %s", (id,))
                    db.commit()
                    
                    if cur.rowcount > 0:
                        messagebox.showinfo("Done", "Deleted!")
                    else:
                        messagebox.showinfo("Not Found", "No such ID.")
                    win.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"Can't delete: {str(e)}")
        
        btn_frm = ttk.Frame(cnt, style='TFrame')
        btn_frm.pack(pady=20)
        
        sub_btn = ttk.Button(btn_frm, text="Del", command=sub, style='TButton')
        sub_btn.pack(pady=10)
    else:
        messagebox.showerror("Denied", "Wrong Password!")

# Show Profit
def prof():
    pw = simpledialog.askstring("Login", "Password:", show='*')
    if pw == pwd:
        try:
            cur.execute("SELECT SUM(g_tot) FROM tkt")
            res = cur.fetchone()
            tot = res[0] if res and res[0] is not None else 0
            
            # Profit window
            win = tk.Toplevel(root)
            win.title("Profit")
            win.geometry("400x200")
            win.configure(bg=SEC)
            
            # Display profit
            ttl = tk.Label(win, text="Total Profit", 
                                  font=sub_f, bg=SEC, fg=PRIM)
            ttl.pack(pady=20)
            
            prf = ttk.Frame(win, style='TFrame')
            prf.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
            
            amt = tk.Label(prf, 
                                   text=f"₹{tot:,.2f}", 
                                   font=("Helvetica", 24, "bold"),
                                   bg=SEC,
                                   fg=ACC)
            amt.pack(pady=10)
            
            cls_btn = ttk.Button(win, text="Close", 
                                  command=win.destroy, style='TButton')
            cls_btn.pack(pady=10)
            
        except Exception as e:
            messagebox.showerror("Error", f"Can't get data!\n{str(e)}")
    else:
        messagebox.showerror("Denied", "Wrong Password!")

# Reset Password
def rpwd():
    win, cnt = mk_win("New Password", wid=400, hgt=300)
    
    ph = mk_fld(cnt, "Phone")
    dob = mk_fld(cnt, "DOB (YYYY-MM-DD)")
    npw = mk_fld(cnt, "New Password")
    
    # Hide password
    npw.configure(show="*")
    
    def sub():
        global pwd
        if ph.get() == OWN_PH and dob.get() == OWN_DOB:
            pwd = npw.get()
            messagebox.showinfo("Done", "Password Changed!")
            win.destroy()
        else:
            messagebox.showerror("Error", "Wrong Info!")
    
    btn_frm = ttk.Frame(cnt, style='TFrame')
    btn_frm.pack(pady=20)
    
    sub_btn = ttk.Button(btn_frm, text="Change", command=sub, style='TButton')
    sub_btn.pack(pady=10)

# Exit function - properly closes database connection before exiting
def exit():
    if db.is_connected():
        cur.close()
        db.close()
    root.destroy()

# Main Buttons
mk_btn(btn_frm, "Add Customer", reg)
mk_btn(btn_frm, "Book Ticket", book)
mk_btn(btn_frm, "Show Bill", bill)
mk_btn(btn_frm, "All Customers", all)
mk_btn(btn_frm, "Delete Customer", dele)
mk_btn(btn_frm, "Total Profit", prof)
mk_btn(btn_frm, "Change Password", rpwd)
mk_btn(btn_frm, "Exit", exit)  # Using the new exit function

# Footer
ftr = ttk.Frame(root, style='TFrame')
ftr.pack(fill=tk.X, side=tk.BOTTOM, pady=10)

ftr_txt = tk.Label(ftr, 
                      text="© 2025 Air Ticket System", 
                      font=lbl_f,
                      bg=SEC,
                      fg=TXT)
ftr_txt.pack(pady=5)

root.mainloop()
