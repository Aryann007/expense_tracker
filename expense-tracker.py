import tkinter as tk
from tkinter import ttk, messagebox
import csv
import os
from datetime import datetime
from collections import defaultdict
import locale

locale.setlocale(locale.LC_ALL, '')

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
FILENAME = os.path.join(SCRIPT_DIR, 'expenses.csv')

CATEGORIES = ["Food", "Transport", "Entertainment", "Housing", "Utilities", "Shopping", "Health", "Other"]
COLORS = {
    "bg": "#f8f9fa",
    "accent": "#4361ee",
    "text": "#212529",
    "light_text": "#6c757d",
    "border": "#dee2e6"
}

def initialize_file():
    try:
        if not os.path.exists(FILENAME):
            with open(FILENAME, mode='w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(['Date', 'Category', 'Amount'])
        elif os.stat(FILENAME).st_size == 0:
            with open(FILENAME, mode='w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(['Date', 'Category', 'Amount'])
    except Exception as e:
        messagebox.showerror("Error", f"Could not initialize file: {str(e)}")
        return False
    return True

def add_expense(date, category, amount):
    try:
        with open(FILENAME, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([date, category, amount])
        return True
    except Exception as e:
        messagebox.showerror("Error", f"Could not add expense: {str(e)}")
        return False

def read_expenses():
    expenses = []
    try:
        if not os.path.exists(FILENAME):
            return expenses
        
        with open(FILENAME, mode='r') as file:
            reader = csv.reader(file)
            next(reader, None)
            
            for row in reader:
                if not row:
                    continue
                expenses.append(row)
    except Exception as e:
        messagebox.showerror("Error", f"Could not read expenses: {str(e)}")
    
    return expenses

def submit_expense():
    category = category_var.get()
    amount = amount_entry.get()
    date = date_entry.get()

    if not category or not amount or not date or category == "Category" or amount == "Amount":
        messagebox.showerror("Error", "All fields are required")
        return

    try:
        float(amount)
    except ValueError:
        messagebox.showerror("Error", "Please enter a valid amount")
        return
        
    try:
        datetime.strptime(date, "%d-%m-%Y")
    except ValueError:
        messagebox.showerror("Error", "Please enter a valid date in format DD-MM-YYYY")
        return

    if add_expense(date, category, amount):
        amount_entry.delete(0, tk.END)
        amount_entry.insert(0, "Amount")
        date_entry.delete(0, tk.END)
        set_today_date()
        category_combo.focus()

        update_table()
        update_summary()
        status_var.set(f"Added: {category} - ₹{float(amount):.2f}")

def update_table():
    for row in expense_table.get_children():
        expense_table.delete(row)

    expenses = read_expenses()
    for expense in expenses[-100:]:
        date, category, amount = expense
        try:
            formatted_amount = f"₹{float(amount):,.2f}"
            expense_table.insert('', 0, values=(date, category, formatted_amount))
        except ValueError:
            pass

def update_summary():
    total = 0.0
    category_summary = defaultdict(float)
    monthly_summary = defaultdict(float)

    for expense in read_expenses():
        if len(expense) < 3:
            continue
            
        date, category, amount = expense
        try:
            amount_float = float(amount)
            total += amount_float
            category_summary[category] += amount_float
            
            try:
                expense_date = datetime.strptime(date, "%d-%m-%Y")
                month_year = expense_date.strftime("%b %Y")
                monthly_summary[month_year] += amount_float
            except ValueError:
                pass
        except ValueError:
            continue

    total_var.set(f"Total: ₹{total:,.2f}")

    for widget in category_frame.winfo_children():
        widget.destroy()
    for widget in monthly_frame.winfo_children():
        widget.destroy()

    row = 0
    for cat, amt in sorted(category_summary.items(), key=lambda x: x[1], reverse=True):
        percentage = (amt / total * 100) if total > 0 else 0
        
        cat_row = tk.Frame(category_frame, bg=COLORS["bg"])
        cat_row.pack(fill="x", pady=5)
        
        tk.Label(cat_row, text=f"{cat}", font=("Helvetica", 10), 
                 bg=COLORS["bg"], fg=COLORS["text"], anchor="w").pack(side="left")
        
        tk.Label(cat_row, text=f"₹{amt:,.2f} ({percentage:.1f}%)", font=("Helvetica", 10),
                 bg=COLORS["bg"], fg=COLORS["light_text"], anchor="e").pack(side="right")
        
        row += 1

    row = 0
    for month, amt in sorted(monthly_summary.items(), 
                            key=lambda x: datetime.strptime(x[0], "%b %Y") if x[0] else datetime.now(), 
                            reverse=True)[:4]:
        if not month:
            continue
            
        month_row = tk.Frame(monthly_frame, bg=COLORS["bg"])
        month_row.pack(fill="x", pady=5)
        
        tk.Label(month_row, text=f"{month}", font=("Helvetica", 10),
                 bg=COLORS["bg"], fg=COLORS["text"], anchor="w").pack(side="left")
        
        tk.Label(month_row, text=f"₹{amt:,.2f}", font=("Helvetica", 10),
                 bg=COLORS["bg"], fg=COLORS["light_text"], anchor="e").pack(side="right")
        
        row += 1

def set_today_date():
    today = datetime.now().strftime("%d-%m-%Y")
    date_entry.delete(0, tk.END)
    date_entry.insert(0, today)

def main():
    global root, category_var, amount_entry, date_entry, status_var
    global expense_table, total_var, category_frame, monthly_frame, category_combo
    
    root = tk.Tk()
    root.title("Expense Tracker")
    root.geometry("750x600")
    root.configure(bg=COLORS["bg"])
    root.option_add("*Font", "Helvetica 10")

    style = ttk.Style()
    style.theme_use('clam')
    style.configure(".", background=COLORS["bg"], foreground=COLORS["text"])
    style.configure("TFrame", background=COLORS["bg"])
    style.configure("TLabel", background=COLORS["bg"], foreground=COLORS["text"])
    style.configure("TButton", background=COLORS["accent"], foreground="white", padding=6)
    style.map("TButton", background=[("active", "#3051D3")])
    style.configure("Accent.TButton", background=COLORS["accent"], foreground="white", padding=8)
    
    style.configure("Treeview", 
                    background="white", 
                    foreground=COLORS["text"],
                    fieldbackground="white", 
                    rowheight=28)
    style.configure("Treeview.Heading", 
                    background=COLORS["bg"], 
                    foreground=COLORS["text"],
                    font=("Helvetica", 10, "bold"))
    style.map("Treeview", background=[("selected", COLORS["accent"])])

    if not initialize_file():
        root.destroy()
        return

    main_frame = ttk.Frame(root, padding=20)
    main_frame.pack(fill="both", expand=True)

    header_frame = ttk.Frame(main_frame)
    header_frame.pack(fill="x", pady=(0, 20))

    tk.Label(header_frame, text="Expense Tracker", 
             font=("Helvetica", 18, "bold"), 
             bg=COLORS["bg"], 
             fg=COLORS["accent"]).pack(side="left")

    input_frame = ttk.Frame(main_frame)
    input_frame.pack(fill="x", pady=(0, 15))
    
    category_var = tk.StringVar()
    category_combo = ttk.Combobox(input_frame, textvariable=category_var, width=15, values=CATEGORIES)
    category_combo.grid(row=0, column=0, padx=(0, 10))
    category_combo.set("Category")

    amount_entry = ttk.Entry(input_frame, width=12, justify="right")
    amount_entry.insert(0, "Amount")
    amount_entry.grid(row=0, column=1, padx=(0, 10))
    
    date_frame = ttk.Frame(input_frame)
    date_frame.grid(row=0, column=2, padx=(0, 10))
    
    date_entry = ttk.Entry(date_frame, width=12)
    date_entry.pack(side="left")
    
    today_btn = ttk.Button(date_frame, text="Today", width=6, command=set_today_date)
    today_btn.pack(side="left", padx=2)
    
    submit_btn = ttk.Button(input_frame, text="Add", style="Accent.TButton", command=submit_expense)
    submit_btn.grid(row=0, column=3, padx=(10, 0))
    
    input_frame.columnconfigure(3, weight=1)

    status_var = tk.StringVar()
    status_var.set("Ready")
    status_label = ttk.Label(main_frame, textvariable=status_var, foreground=COLORS["light_text"])
    status_label.pack(fill="x", pady=(0, 10))

    notebook = ttk.Notebook(main_frame)
    notebook.pack(fill="both", expand=True)
    
    expenses_tab = ttk.Frame(notebook, padding=10)
    notebook.add(expenses_tab, text="Expenses")
    
    table_frame = ttk.Frame(expenses_tab)
    table_frame.pack(fill="both", expand=True)
    
    columns = ("Date", "Category", "Amount")
    expense_table = ttk.Treeview(table_frame, columns=columns, show='headings', height=15)
    
    expense_table.heading("Date", text="Date")
    expense_table.heading("Category", text="Category")
    expense_table.heading("Amount", text="Amount")
    
    expense_table.column("Date", width=100)
    expense_table.column("Category", width=120)
    expense_table.column("Amount", width=100, anchor="e")
    
    table_scroll = ttk.Scrollbar(table_frame, orient="vertical", command=expense_table.yview)
    expense_table.configure(yscrollcommand=table_scroll.set)
    
    expense_table.pack(side="left", fill="both", expand=True)
    table_scroll.pack(side="right", fill="y")
    
    summary_tab = ttk.Frame(notebook, padding=10)
    notebook.add(summary_tab, text="Summary")
    
    total_var = tk.StringVar()
    total_var.set("Total: ₹0.00")
    total_label = tk.Label(summary_tab, 
                           textvariable=total_var, 
                           font=("Helvetica", 16, "bold"), 
                           bg=COLORS["bg"], 
                           fg=COLORS["accent"])
    total_label.pack(pady=(0, 20))
    
    summary_columns = ttk.Frame(summary_tab)
    summary_columns.pack(fill="both", expand=True)
    
    cat_section = ttk.Frame(summary_columns, padding=10)
    cat_section.pack(side="left", fill="both", expand=True, padx=(0, 10))
    
    cat_heading = tk.Label(cat_section, text="Category Breakdown", 
                         font=("Helvetica", 12, "bold"), 
                         bg=COLORS["bg"], fg=COLORS["text"])
    cat_heading.pack(anchor="w", pady=(0, 10))
    
    ttk.Separator(cat_section, orient="horizontal").pack(fill="x", pady=5)
    
    category_frame = tk.Frame(cat_section, bg=COLORS["bg"])
    category_frame.pack(fill="both", expand=True)
    
    month_section = ttk.Frame(summary_columns, padding=10)
    month_section.pack(side="right", fill="both", expand=True, padx=(10, 0))
    
    month_heading = tk.Label(month_section, text="Monthly Trend", 
                           font=("Helvetica", 12, "bold"), 
                           bg=COLORS["bg"], fg=COLORS["text"])
    month_heading.pack(anchor="w", pady=(0, 10))
    
    ttk.Separator(month_section, orient="horizontal").pack(fill="x", pady=5)
    
    monthly_frame = tk.Frame(month_section, bg=COLORS["bg"])
    monthly_frame.pack(fill="both", expand=True)

    set_today_date()
    update_table()
    update_summary()
    
    category_combo.focus_set()
    
    def on_entry_click(event, entry, default_text):
        if entry.get() == default_text:
            entry.delete(0, "end")
            
    def on_focusout(event, entry, default_text):
        if entry.get() == '':
            entry.insert(0, default_text)
            
    amount_entry.bind("<FocusIn>", lambda event: on_entry_click(event, amount_entry, "Amount"))
    amount_entry.bind("<FocusOut>", lambda event: on_focusout(event, amount_entry, "Amount"))

    root.mainloop()

if __name__ == "__main__":
    main()
