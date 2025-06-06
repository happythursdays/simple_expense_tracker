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
def load_exp_list():
    if os.path.exists(EXPENSES_FILE):
        with open(EXPENSES_FILE, "r") as f:
            return json.load(f)
    return []


def save_exp_list(data):
    with open(EXPENSES_FILE, "w") as f:
        json.dump(data, f, indent=4)


# --------- Main App ---------
class ExpenseTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("Simple Expense Tracker")
        self.root.configure(bg="#f4f4f4")

        self.exp_list = load_exp_list()
        self.filt_exp_list = self.exp_list[:]
        self.sel_idx = None

        self.setup_widgets()
        self.refresh_table()

    def setup_widgets(self):
        inp_frame = tk.Frame(self.root, bg="#f4f4f4")
        inp_frame.pack(pady=10)

        tk.Label(inp_frame, text="Date (YYYY-MM-DD):", bg="#f4f4f4").grid(row=0, column=0, padx=5, sticky="e")
        self.dt_ent = tk.Entry(inp_frame)
        self.dt_ent.grid(row=0, column=1, padx=5)

        tk.Label(inp_frame, text="Category:", bg="#f4f4f4").grid(row=0, column=2, padx=5, sticky="e")
        self.cat_var = tk.StringVar()
        self.cat_drop = ttk.Combobox(inp_frame, textvariable=self.cat_var, values=CATEGORIES, state="readonly")
        self.cat_drop.grid(row=0, column=3, padx=5)
        self.cat_drop.current(0)

        tk.Label(inp_frame, text="Description:", bg="#f4f4f4").grid(row=1, column=0, padx=5, sticky="e")
        self.desc_ent = tk.Entry(inp_frame, width=40)
        self.desc_ent.grid(row=1, column=1, columnspan=3, padx=5)

        tk.Label(inp_frame, text="Amount (₱):", bg="#f4f4f4").grid(row=2, column=0, padx=5, sticky="e")
        self.amt_ent = tk.Entry(inp_frame)
        self.amt_ent.grid(row=2, column=1, padx=5)

        self.add_btn = tk.Button(inp_frame, text="Add Expense", command=self.add_exps, bg="#5cb85c", fg="white")
        self.add_btn.grid(row=2, column=3, pady=5)

        self.upd_btn = tk.Button(inp_frame, text="Update Selected", command=self.mod_exps, bg="#0275d8", fg="white")
        self.upd_btn.grid(row=2, column=2, pady=5)

        self.del_btn = tk.Button(inp_frame, text="Delete Selected", command=self.del_exps, bg="#d9534f", fg="white")
        self.del_btn.grid(row=2, column=4, padx=5)

        srch_frame = tk.LabelFrame(self.root, text="Search / Filter", bg="#f4f4f4", padx=10, pady=5)
        srch_frame.pack(padx=10, pady=10, fill="x")

        tk.Label(srch_frame, text="Date or Keyword:", bg="#f4f4f4").grid(row=0, column=0, padx=5)
        self.srch_ent = tk.Entry(srch_frame, width=25)
        self.srch_ent.grid(row=0, column=1, padx=5)

        tk.Label(srch_frame, text="Category:", bg="#f4f4f4").grid(row=0, column=2, padx=5)
        self.filt_cat_var = tk.StringVar()
        filt_cat_list = ["All"] + CATEGORIES
        self.filt_drop = ttk.Combobox(srch_frame, textvariable=self.filt_cat_var, values=filt_cat_list, state="readonly", width=15)
        self.filt_drop.grid(row=0, column=3, padx=5)
        self.filt_drop.current(0)

        tk.Button(srch_frame, text="Search", command=self.search_exps, bg="#f0ad4e").grid(row=0, column=4, padx=5)
        tk.Button(srch_frame, text="Reset", command=self.ShAll_expenses, bg="#6c757d", fg="white").grid(row=0, column=5, padx=5)

        self.tree = ttk.Treeview(self.root, columns=("Date", "Category", "Description", "Amount"), show="headings")
        for col in self.tree["columns"]:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor="center")
        self.tree.bind("<<TreeviewSelect>>", self.on_select)
        self.tree.pack(padx=10, pady=10, fill="both", expand=True)

        self.total_lbl = tk.Label(self.root, text="", font=("Arial", 12), bg="#f4f4f4", fg="#333")
        self.total_lbl.pack(pady=5)

    def refresh_table(self):
        self.tree.delete(*self.tree.get_children())
        total = 0
        for ex in self.filt_exp_list:
            self.tree.insert("", "end", values=(ex["date"], ex["category"], ex["description"], f"₱{ex['amount']:.2f}"))
            total += ex["amount"]
        self.total_lbl.config(text=f"Total: ₱{total:.2f}")

    def add_exps(self):
        try:
            dt = datetime.strptime(self.dt_ent.get(), "%Y-%m-%d").strftime("%Y-%m-%d")
            cat = self.cat_var.get()
            desc = self.desc_ent.get().strip()
            amt = float(self.amt_ent.get())
            if not desc:
                raise ValueError("Description required")
            self.exp_list.append({"date": dt, "category": cat, "description": desc, "amount": amt})
            save_exp_list(self.exp_list)
            self.ShAll_expenses()
            self.clear_inputs()
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter valid data (e.g. YYYY-MM-DD for date, number for amount)")

    def on_select(self, event):
        sel = self.tree.selection()
        if sel:
            idx = self.tree.index(sel[0])
            self.sel_idx = idx
            ex = self.filt_exp_list[idx]

            self.dt_ent.delete(0, tk.END)
            self.dt_ent.insert(0, ex["date"])

            self.cat_var.set(ex["category"])

            self.desc_ent.delete(0, tk.END)
            self.desc_ent.insert(0, ex["description"])

            self.amt_ent.delete(0, tk.END)
            self.amt_ent.insert(0, str(ex["amount"]))

    def mod_exps(self):
        if self.sel_idx is None:
            messagebox.showwarning("No selection", "Please select an expense to update.")
            return
        try:
            dt = datetime.strptime(self.dt_ent.get(), "%Y-%m-%d").strftime("%Y-%m-%d")
            cat = self.cat_var.get()
            desc = self.desc_ent.get().strip()
            amt = float(self.amt_ent.get())

            full_idx = self.exp_list.index(self.filt_exp_list[self.sel_idx])
            self.exp_list[full_idx] = {"date": dt, "category": cat, "description": desc, "amount": amt}
            save_exp_list(self.exp_list)
            self.ShAll_expenses()
            self.clear_inputs()
            self.sel_idx = None
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter valid data (e.g. YYYY-MM-DD for date, number for amount)")

    def del_exps(self):
        if self.sel_idx is None:
            messagebox.showwarning("No selection", "Please select an expense to delete.")
            return
        confirm = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this expense?")
        if confirm:
            del self.exp_list[self.exp_list.index(self.filt_exp_list[self.sel_idx])]
            save_exp_list(self.exp_list)
            self.ShAll_expenses()
            self.clear_inputs()
            self.sel_idx = None

    def clear_inputs(self):
        self.dt_ent.delete(0, tk.END)
        self.desc_ent.delete(0, tk.END)
        self.amt_ent.delete(0, tk.END)
        self.cat_drop.current(0)

    def search_exps(self):
        key = self.srch_ent.get().strip().lower()
        cat = self.filt_cat_var.get()

        def match(ex):
            return (
                (key in ex["description"].lower() or key in ex["date"]) and
                (cat == "All" or ex["category"] == cat)
            )

        self.filt_exp_list = list(filter(match, self.exp_list))
        self.refresh_table()

    def ShAll_expenses(self):
        self.filt_exp_list = self.exp_list[:]
        self.srch_ent.delete(0, tk.END)
        self.filt_drop.current(0)
        self.refresh_table()


if __name__ == "__main__":
    root = tk.Tk()
    app = ExpenseTracker(root)
    root.mainloop()
