import csv
import os
from datetime import datetime
from collections import defaultdict
import locale

locale.setlocale(locale.LC_ALL, '')

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
FILENAME = os.path.join(SCRIPT_DIR, 'expenses.csv')

CATEGORIES = ["Food", "Transport", "Entertainment", "Housing", "Utilities", "Shopping", "Health", "Other"]

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
        print(f"Error: Could not initialize file: {str(e)}")
        return False
    return True

def add_expense(date, category, amount):
    try:
        with open(FILENAME, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([date, category, amount])
        return True
    except Exception as e:
        print(f"Error: Could not add expense: {str(e)}")
        return False

def read_expenses():
    expenses = []
    try:
        if not os.path.exists(FILENAME):
            return expenses
        
        with open(FILENAME, mode='r') as file:
            reader = csv.reader(file)
            next(reader, None)  # Skip header
            
            for row in reader:
                if not row:  # Skip empty rows
                    continue
                expenses.append(row)
    except Exception as e:
        print(f"Error: Could not read expenses: {str(e)}")
    
    return expenses

def get_total():
    total = 0.0
    for expense in read_expenses():
        if len(expense) < 3:
            continue
        try:
            amount = float(expense[2])
            total += amount
        except ValueError:
            continue
    return total

def get_category_summary():
    category_summary = defaultdict(float)
    for expense in read_expenses():
        if len(expense) < 3:
            continue
        date, category, amount = expense
        try:
            amount_float = float(amount)
            category_summary[category] += amount_float
        except ValueError:
            continue
    return category_summary

def get_monthly_summary():
    monthly_summary = defaultdict(float)
    for expense in read_expenses():
        if len(expense) < 3:
            continue
        date, category, amount = expense
        try:
            amount_float = float(amount)
            try:
                expense_date = datetime.strptime(date, "%d-%m-%Y")
                month_year = expense_date.strftime("%b %Y")
                monthly_summary[month_year] += amount_float
            except ValueError:
                pass
        except ValueError:
            continue
    return monthly_summary

def print_expenses(limit=None):
    expenses = read_expenses()
    if limit:
        expenses = expenses[-limit:]
    
    print("\n===== EXPENSES =====")
    print("Date        | Category      | Amount")
    print("-" * 40)
    
    for expense in expenses:
        if len(expense) < 3:
            continue
        date, category, amount = expense
        try:
            formatted_amount = f"₹{float(amount):,.2f}"
            print(f"{date:<11} | {category:<13} | {formatted_amount:>10}")
        except ValueError:
            continue

def print_summary():
    total = get_total()
    category_summary = get_category_summary()
    monthly_summary = get_monthly_summary()
    
    print("\n===== SUMMARY =====")
    print(f"Total Expenses: ₹{total:,.2f}")
    
    print("\nCategory Breakdown:")
    print("-" * 40)
    for cat, amt in sorted(category_summary.items(), key=lambda x: x[1], reverse=True):
        percentage = (amt / total * 100) if total > 0 else 0
        print(f"{cat:<15} ₹{amt:,.2f} ({percentage:.1f}%)")
    
    print("\nMonthly Trend (Last 4 months):")
    print("-" * 40)
    count = 0
    for month, amt in sorted(monthly_summary.items(), 
                          key=lambda x: datetime.strptime(x[0], "%b %Y") if x[0] else datetime.now(), 
                          reverse=True):
        if not month:
            continue
        print(f"{month:<10} ₹{amt:,.2f}")
        count += 1
        if count >= 4:
            break

def validate_date(date_str):
    try:
        datetime.strptime(date_str, "%d-%m-%Y")
        return True
    except ValueError:
        return False

def validate_amount(amount_str):
    try:
        float(amount_str)
        return True
    except ValueError:
        return False

def get_today_date():
    return datetime.now().strftime("%d-%m-%Y")

def main():
    if not initialize_file():
        print("Failed to initialize expense file.")
        return
    
    while True:
        print("\n===== EXPENSE TRACKER =====")
        print("1. Add Expense")
        print("2. View Expenses")
        print("3. View Summary")
        print("4. Exit")
        
        choice = input("Enter your choice (1-4): ")
        
        if choice == '1':
            # Add expense
            print("\nAdd New Expense:")
            print("Available categories:", ", ".join(CATEGORIES))
            
            category = input("Category: ")
            while category not in CATEGORIES:
                print(f"Invalid category. Please choose from: {', '.join(CATEGORIES)}")
                category = input("Category: ")
            
            amount = input("Amount: ")
            while not validate_amount(amount):
                print("Invalid amount. Please enter a valid number.")
                amount = input("Amount: ")
            
            date = input(f"Date (DD-MM-YYYY) [Today: {get_today_date()}]: ")
            if not date:
                date = get_today_date()
            while not validate_date(date):
                print("Invalid date format. Please use DD-MM-YYYY.")
                date = input(f"Date (DD-MM-YYYY) [Today: {get_today_date()}]: ")
                if not date:
                    date = get_today_date()
            
            if add_expense(date, category, amount):
                print(f"Expense added: {category} - ₹{float(amount):.2f}")
        
        elif choice == '2':
            # View expenses
            limit_str = input("How many recent expenses to show? (leave blank for all): ")
            limit = None
            if limit_str:
                try:
                    limit = int(limit_str)
                except ValueError:
                    print("Invalid input. Showing all expenses.")
            
            print_expenses(limit)
        
        elif choice == '3':
            # View summary
            print_summary()
        
        elif choice == '4':
            # Exit
            print("Thank you for using Expense Tracker. Goodbye!")
            break
        
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()