import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import datetime

class CafeYouthBilling:
    def __init__(self, root):
        self.root = root
        self.root.title("Cafe Youth - Internal Management System")
        self.root.geometry("1100x700")
        
        self.setup_database()
        
        self.cart_items = []
        self.all_menu_items = []

        # --- NAVIGATION BAR ---
        nav_frame = tk.Frame(root, bg="#3C3489", pady=10)
        nav_frame.pack(fill="x")
        
        tk.Label(nav_frame, text="CAFE YOUTH MANAGEMENT", font=("Arial", 18, "bold"), bg="#3C3489", fg="white").pack(side="left", padx=20)
        tk.Button(nav_frame, text="📊 VIEW DAILY REPORTS", command=self.open_reports, bg="#FAC775", fg="black", font=("Arial", 10, "bold")).pack(side="right", padx=20)

        # --- MAIN LAYOUT ---
        main_frame = tk.Frame(root, padx=20, pady=20)
        main_frame.pack(fill="both", expand=True)

        # LEFT SIDE: Menu Search
        left_frame = tk.LabelFrame(main_frame, text=" 1. Search & Add Items ", padx=10, pady=10)
        left_frame.pack(side="left", fill="both", expand=True, padx=5)

        self.search_var = tk.StringVar()
        self.search_var.trace("w", self.update_menu_list)
        tk.Entry(left_frame, textvariable=self.search_var, font=("Arial", 12)).pack(fill="x", pady=5)

        self.menu_tree = ttk.Treeview(left_frame, columns=("Name", "Price"), show="headings")
        self.menu_tree.heading("Name", text="Item Name")
        self.menu_tree.heading("Price", text="Price")
        self.menu_tree.pack(fill="both", expand=True)
        
        add_ctrl_frame = tk.Frame(left_frame)
        add_ctrl_frame.pack(fill="x", pady=10)
        
        tk.Label(add_ctrl_frame, text="Qty:").pack(side="left")
        self.qty_var = tk.StringVar(value="1")
        tk.Entry(add_ctrl_frame, textvariable=self.qty_var, width=5, font=("Arial", 12)).pack(side="left", padx=5)
        tk.Button(add_ctrl_frame, text="ADD TO ORDER", command=self.add_to_cart, bg="#0F6E56", fg="white", font=("Arial", 11, "bold")).pack(side="right", fill="x", expand=True)

        # RIGHT SIDE: Current Order
        right_frame = tk.LabelFrame(main_frame, text=" 2. Current Order ", padx=10, pady=10)
        right_frame.pack(side="right", fill="both", expand=True, padx=5)

        self.cart_tree = ttk.Treeview(right_frame, columns=("Item", "Qty", "Total"), show="headings")
        self.cart_tree.heading("Item", text="Item Name")
        self.cart_tree.heading("Qty", text="Qty")
        self.cart_tree.heading("Total", text="Total")
        self.cart_tree.pack(fill="both", expand=True)
        
        self.cart_tree.bind("<Double-1>", lambda e: self.remove_selected())
        tk.Button(right_frame, text="REMOVE SELECTED ITEM", command=self.remove_selected, bg="#993C1D", fg="white").pack(fill="x", pady=5)

        self.total_label = tk.Label(right_frame, text="Total: ₹0.00", font=("Arial", 22, "bold"), pady=10)
        self.total_label.pack()

        tk.Button(right_frame, text="CONFIRM & SAVE ORDER", command=self.save_order, bg="#3C3489", fg="white", font=("Arial", 14, "bold"), pady=15).pack(fill="x")
        
        self.load_menu_from_db()

    def setup_database(self):
        conn = sqlite3.connect('cafe.db')
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS sales 
                          (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                           item_name TEXT, 
                           quantity INTEGER, 
                           total_price REAL, 
                           date TEXT)''')
        conn.commit()
        conn.close()

    def load_menu_from_db(self):
        conn = sqlite3.connect('cafe.db')
        raw_items = conn.execute("SELECT name, price FROM menu").fetchall()
        conn.close()

        # --- TEMPORARY PRICE HIKE LOOP START ---
        self.all_menu_items = []
        for name, price in raw_items:
            if price <= 150:
                new_price = price + 20
            else:
                new_price = price + 30
            self.all_menu_items.append((name, new_price))
        # --- TEMPORARY PRICE HIKE LOOP END ---

        self.update_menu_list()

    def update_menu_list(self, *args):
        search_term = self.search_var.get().lower()
        for i in self.menu_tree.get_children(): self.menu_tree.delete(i)
        for name, price in self.all_menu_items:
            if search_term in name.lower():
                self.menu_tree.insert("", "end", values=(name, f"₹{price}"))

    def add_to_cart(self):
        selected = self.menu_tree.selection()
        if not selected: return
        item_data = self.menu_tree.item(selected[0])['values']
        name = item_data[0]
        price = float(item_data[1].replace('₹', ''))
        try:
            qty = int(self.qty_var.get())
            self.cart_items.append({"name": name, "qty": qty, "total": price * qty})
            self.cart_tree.insert("", "end", values=(name, qty, f"₹{price*qty}"))
            self.update_total()
            self.qty_var.set("1")
        except: messagebox.showerror("Error", "Check Quantity")

    def remove_selected(self):
        selected_item = self.cart_tree.selection()
        if not selected_item: return
        index = self.cart_tree.index(selected_item[0])
        self.cart_items.pop(index)
        self.cart_tree.delete(selected_item[0])
        self.update_total()

    def update_total(self):
        total = sum(item['total'] for item in self.cart_items)
        self.total_label.config(text=f"Total: ₹{total:.2f}")

    def save_order(self):
        if not self.cart_items: return
        try:
            conn = sqlite3.connect('cafe.db')
            cursor = conn.cursor()
            # We save the date in YYYY-MM-DD format for easy filtering
            now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            for item in self.cart_items:
                cursor.execute("INSERT INTO sales (item_name, quantity, total_price, date) VALUES (?, ?, ?, ?)",
                               (item['name'], item['qty'], item['total'], now))
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", "Order recorded!")
            self.clear_all()
        except Exception as e: messagebox.showerror("Error", str(e))

    def clear_all(self):
        self.cart_items = []
        for i in self.cart_tree.get_children(): self.cart_tree.delete(i)
        self.update_total()

    # --- UPDATED REPORT WINDOW ---
    def open_reports(self):
        report_win = tk.Toplevel(self.root)
        report_win.title("Cafe Youth - Sales Insights")
        report_win.geometry("800x650")
        
        today_date = datetime.datetime.now().strftime("%Y-%m-%d")
        
        conn = sqlite3.connect('cafe.db')
        cursor = conn.cursor()

        # 1. Calculation: Today's Sales
        # We use 'LIKE today_date%' to find all timestamps from today
        cursor.execute("SELECT SUM(total_price) FROM sales WHERE date LIKE ?", (f"{today_date}%",))
        today_total = cursor.fetchone()[0] or 0.0

        # 2. Calculation: Lifetime Sales
        cursor.execute("SELECT SUM(total_price) FROM sales")
        lifetime_total = cursor.fetchone()[0] or 0.0

        # UI for Totals
        tk.Label(report_win, text=f"DATE: {today_date}", font=("Arial", 12, "bold")).pack(pady=5)
        
        summary_frame = tk.Frame(report_win, pady=10)
        summary_frame.pack()
        
        tk.Label(summary_frame, text=f"TODAY'S SALE: ₹{today_total:.2f}", font=("Arial", 18, "bold"), fg="green").grid(row=0, column=0, padx=20)
        tk.Label(summary_frame, text=f"LIFETIME: ₹{lifetime_total:.2f}", font=("Arial", 14), fg="gray").grid(row=0, column=1, padx=20)

        # 3. Today's Transaction Table
        tk.Label(report_win, text="Today's Individual Orders:", font=("Arial", 11, "bold")).pack(pady=10)
        
        tree = ttk.Treeview(report_win, columns=("Item", "Qty", "Total", "Time"), show="headings")
        tree.heading("Item", text="Item Name")
        tree.heading("Qty", text="Qty")
        tree.heading("Total", text="Amount")
        tree.heading("Time", text="Time")
        tree.pack(fill="both", expand=True, padx=20, pady=5)

        # Fetch today's data sorted by latest first
        cursor.execute("SELECT item_name, quantity, total_price, date FROM sales WHERE date LIKE ? ORDER BY id DESC", (f"{today_date}%",))
        for row in cursor.fetchall():
            # row[3] is "2023-10-27 14:30:00", we just show the time "14:30:00"
            time_only = row[3].split(" ")[1]
            tree.insert("", "end", values=(row[0], row[1], f"₹{row[2]}", time_only))

        conn.close()
        tk.Button(report_win, text="CLOSE", command=report_win.destroy, width=20).pack(pady=10)

if __name__ == "__main__":
    root = tk.Tk()
    app = CafeYouthBilling(root)
    root.mainloop()