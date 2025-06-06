"""
expense_tracker.py
Simple Expense Tracker
Author: Jamie Nicole Benwick
Version: 06/06/2025
"""

import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from datetime import datetime

EXPENSES_FILE = "expenses.json"
CATEGORIES = ["Food", "Transport", "Utilities", "Shopping", "Entertainment", "Other"]


# --------- Data Handling ---------
def load_expenses():
    if os.path.exists(EXPENSES_FILE):
        with open(EXPENSES_FILE, "r") as file:
            return json.load(file)
    return []


def save_expenses(data):
    with open(EXPENSES_FILE, "w") as file:
        json.dump(data, file, indent=4)


# --------- Main App ---------
class ExpenseTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("Simple Expense Tracker")
        self.root.configure(bg="#f4f4f4")

        self.expenses = load_expenses()
        self.filtered_expenses = self.expenses[:]
        self.selected_index = None

        self.setup_widgets()
        self.refresh_table()

    def setup_widgets(self):
        # Input Frame
        input_frame = tk.Frame(self.root, bg="#f4f4f4")
        input_frame.pack(pady=10)

        tk.Label(input_frame, text="Date (YYYY-MM-DD):", bg="#f4f4f4").grid(row=0, column=0, padx=5, sticky="e")
        self.date_entry = tk.Entry(input_frame)
        self.date_entry.grid(row=0, column=1, padx=5)

        tk.Label(input_frame, text="Category:", bg="#f4f4f4").grid(row=0, column=2, padx=5, sticky="e")
        self.category_var = tk.StringVar()
        self.category_dropdown = ttk.Combobox(input_frame, textvariable=self.category_var, values=CATEGORIES,
                                              state="readonly")
        self.category_dropdown.grid(row=0, column=3, padx=5)
        self.category_dropdown.current(0)

        tk.Label(input_frame, text="Description:", bg="#f4f4f4").grid(row=1, column=0, padx=5, sticky="e")
        self.desc_entry = tk.Entry(input_frame, width=40)
        self.desc_entry.grid(row=1, column=1, columnspan=3, padx=5)

        tk.Label(input_frame, text="Amount (₱):", bg="#f4f4f4").grid(row=2, column=0, padx=5, sticky="e")
        self.amount_entry = tk.Entry(input_frame)
        self.amount_entry.grid(row=2, column=1, padx=5)

        self.add_btn = tk.Button(input_frame, text="Add Expense", command=self.add_expense, bg="#5cb85c", fg="white")
        self.add_btn.grid(row=2, column=3, pady=5)

        self.update_btn = tk.Button(input_frame, text="Update Selected", command=self.update_expense, bg="#0275d8",
                                    fg="white")
        self.update_btn.grid(row=2, column=2, pady=5)

        self.delete_btn = tk.Button(input_frame, text="Delete Selected", command=self.delete_expense, bg="#d9534f",
                                    fg="white")
        self.delete_btn.grid(row=2, column=4, padx=5)

        # Search/Filter Frame
        search_frame = tk.LabelFrame(self.root, text="Search / Filter", bg="#f4f4f4", padx=10, pady=5)
        search_frame.pack(padx=10, pady=10, fill="x")

        tk.Label(search_frame, text="Date or Keyword:", bg="#f4f4f4").grid(row=0, column=0, padx=5)
        self.search_entry = tk.Entry(search_frame, width=25)
        self.search_entry.grid(row=0, column=1, padx=5)

        tk.Label(search_frame, text="Category:", bg="#f4f4f4").grid(row=0, column=2, padx=5)
        self.filter_cat_var = tk.StringVar()
        filter_categories = ["All"] + CATEGORIES
        self.filter_dropdown = ttk.Combobox(search_frame, textvariable=self.filter_cat_var, values=filter_categories,
                                            state="readonly", width=15)
        self.filter_dropdown.grid(row=0, column=3, padx=5)
        self.filter_dropdown.current(0)

        tk.Button(search_frame, text="Search", command=self.filter_expenses, bg="#f0ad4e").grid(row=0, column=4, padx=5)
        tk.Button(search_frame, text="Reset", command=self.reset_filter, bg="#6c757d", fg="white").grid(row=0, column=5,
                                                                                                        padx=5)

        # Table
        self.tree = ttk.Treeview(self.root, columns=("Date", "Category", "Description", "Amount"), show="headings")
        for col in self.tree["columns"]:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor="center")
        self.tree.bind("<<TreeviewSelect>>", self.on_select)
        self.tree.pack(padx=10, pady=10, fill="both", expand=True)

        # Total Label
        self.total_label = tk.Label(self.root, text="", font=("Arial", 12), bg="#f4f4f4", fg="#333")
        self.total_label.pack(pady=5)

    def refresh_table(self):
        self.tree.delete(*self.tree.get_children())
        total = 0
        for expense in self.filtered_expenses:
            self.tree.insert("", "end", values=(
            expense["date"], expense["category"], expense["description"], f"₱{expense['amount']:.2f}"))
            total += expense["amount"]
        self.total_label.config(text=f"Total: ₱{total:.2f}")

    def add_expense(self):
        try:
            date = datetime.strptime(self.date_entry.get(), "%Y-%m-%d").strftime("%Y-%m-%d")
            category = self.category_var.get()
            desc = self.desc_entry.get().strip()
            amount = float(self.amount_entry.get())

            if not desc:
                raise ValueError("Description required")

            self.expenses.append({"date": date, "category": category, "description": desc, "amount": amount})
            save_expenses(self.expenses)
            self.reset_filter()
            self.clear_inputs()
        except ValueError:
            messagebox.showerror("Invalid Input",
                                 "Please enter valid data (e.g. YYYY-MM-DD for date, number for amount)")

    def on_select(self, event):
        selected = self.tree.selection()
        if selected:
            index = self.tree.index(selected[0])
            self.selected_index = index
            expense = self.filtered_expenses[index]

            self.date_entry.delete(0, tk.END)
            self.date_entry.insert(0, expense["date"])

            self.category_var.set(expense["category"])

            self.desc_entry.delete(0, tk.END)
            self.desc_entry.insert(0, expense["description"])

            self.amount_entry.delete(0, tk.END)
            self.amount_entry.insert(0, str(expense["amount"]))

    def update_expense(self):
        if self.selected_index is None:
            messagebox.showwarning("No selection", "Please select an expense to update.")
            return

        try:
            date = datetime.strptime(self.date_entry.get(), "%Y-%m-%d").strftime("%Y-%m-%d")
            category = self.category_var.get()
            desc = self.desc_entry.get().strip()
            amount = float(self.amount_entry.get())

            full_index = self.expenses.index(self.filtered_expenses[self.selected_index])
            self.expenses[full_index] = {"date": date, "category": category, "description": desc, "amount": amount}
            save_expenses(self.expenses)
            self.reset_filter()
            self.clear_inputs()
            self.selected_index = None
        except ValueError:
            messagebox.showerror("Invalid Input",
                                 "Please enter valid data (e.g. YYYY-MM-DD for date, number for amount)")

    def delete_expense(self):
        if self.selected_index is None:
            messagebox.showwarning("No selection", "Please select an expense to delete.")
            return

        confirm = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this expense?")
        if confirm:
            del self.expenses[self.expenses.index(self.filtered_expenses[self.selected_index])]
            save_expenses(self.expenses)
            self.reset_filter()
            self.clear_inputs()
            self.selected_index = None

    def clear_inputs(self):
        self.date_entry.delete(0, tk.END)
        self.desc_entry.delete(0, tk.END)
        self.amount_entry.delete(0, tk.END)
        self.category_dropdown.current(0)

    def filter_expenses(self):
        keyword = self.search_entry.get().strip().lower()
        category_filter = self.filter_cat_var.get()

        def match(exp):
            return (
                    (keyword in exp["description"].lower() or keyword in exp["date"]) and
                    (category_filter == "All" or exp["category"] == category_filter)
            )

        self.filtered_expenses = list(filter(match, self.expenses))
        self.refresh_table()

    def reset_filter(self):
        self.filtered_expenses = self.expenses[:]
        self.search_entry.delete(0, tk.END)
        self.filter_dropdown.current(0)
        self.refresh_table()


if __name__ == "__main__":
    root = tk.Tk()
    app = ExpenseTracker(root)
    root.mainloop()








