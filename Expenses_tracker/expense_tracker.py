import tkinter as tk
from tkinter import messagebox, ttk
from datetime import date
from pymongo import MongoClient
from bson.objectid import ObjectId


# Step 1: Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["student_expense_tracker"]
collection = db["expenses"]


# Add Expense
def add_expense():
    try:
        amount = float(amount_var.get())
        category = category_var.get().strip()
        description = desc_var.get().strip()

        if not category:
            messagebox.showerror("Error", "Please fill all fields")
            return

        collection.insert_one({
            "Date": date.today().isoformat(),
            "Amount": amount,
            "Category": category,
            "Description": description
        })

        messagebox.showinfo("Success", "Expense Added Successfully!")
        clear_fields()

    except ValueError:
        messagebox.showerror("Error", "Amount must be a number!")


# Clear Entry Fields
def clear_fields():
    amount_var.set("")
    category_var.set("")
    desc_var.set("")



# Show Table with Update/Delete
def show_table(data, title="Data"):
    win = tk.Toplevel(root)
    win.title(title)

    table = ttk.Treeview(win, columns=("Date", "Amount", "Category", "Description"), show="headings")
    for col in ("Date", "Amount", "Category", "Description"):
        table.heading(col, text=col)
        table.column(col, width=120)
    table.pack(fill="both", expand=True)

    id_map = {}  # Store IDs separately

    # Fill table
    for idx, doc in enumerate(data):
        table.insert("", tk.END, iid=str(idx),
                     values=(doc["Date"], doc["Amount"], doc["Category"], doc["Description"]))
        id_map[str(idx)] = str(doc["_id"])

    # Buttons for Update & Delete
    def on_update():
        selected = table.selection()
        if not selected:
            messagebox.showerror("Error", "Select a record to update")
            return
        row_id = selected[0]
        open_update_window(id_map[row_id], table.item(row_id)["values"])

    def on_delete():
        selected = table.selection()
        if not selected:
            messagebox.showerror("Error", "Select a record to delete")
            return
        row_id = selected[0]
        collection.delete_one({"_id": ObjectId(id_map[row_id])})
        messagebox.showinfo("Deleted", "Record deleted successfully!")
        win.destroy()
        show_expenses()

    btn_frame = tk.Frame(win)
    btn_frame.pack(pady=10)
    tk.Button(btn_frame, text="✏ Update", command=on_update, bg="lightgreen").grid(row=0, column=0, padx=5)
    tk.Button(btn_frame, text="🗑 Delete", command=on_delete, bg="lightcoral").grid(row=0, column=1, padx=5)


# Update Window
def open_update_window(record_id, values):
    upd_win = tk.Toplevel(root)
    upd_win.title("Update Expense")

    tk.Label(upd_win, text="Amount (₹):").pack()
    amt = tk.StringVar(value=values[1])
    tk.Entry(upd_win, textvariable=amt).pack()

    tk.Label(upd_win, text="Category:").pack()
    cat = tk.StringVar(value=values[2])
    tk.Entry(upd_win, textvariable=cat).pack()

    tk.Label(upd_win, text="Description:").pack()
    desc = tk.StringVar(value=values[3])
    tk.Entry(upd_win, textvariable=desc).pack()

    def save_update():
        try:
            collection.update_one(
                {"_id": ObjectId(record_id)},
                {"$set": {
                    "Amount": float(amt.get()),
                    "Category": cat.get().strip(),
                    "Description": desc.get().strip()
                }}
            )
            messagebox.showinfo("Success", "Record updated successfully!")
            upd_win.destroy()
        except ValueError:
            messagebox.showerror("Error", "Amount must be a number!")

    tk.Button(upd_win, text="Save", command=save_update, bg="lightgreen").pack(pady=10)


# Show All Expenses

def show_expenses():
    data = collection.find()
    show_table(data, "All Expenses")


# Show Total Spending

def show_total():
    pipeline = [{"$group": {"_id": None, "total": {"$sum": "$Amount"}}}]
    result = list(collection.aggregate(pipeline))
    total = result[0]["total"] if result else 0
    messagebox.showinfo("Total Spending", f"Total Spent: ₹{total:.2f}")


def filter_category():
    def search():
        cat = cat_var.get().strip()
        data = collection.find({"Category": {"$regex": f"^{cat}$", "$options": "i"}})  # case insensitive search
        show_table(data, f"Category: {cat}")

    win = tk.Toplevel(root)
    win.title("Filter by Category")

    tk.Label(win, text="Enter Category:").pack(pady=5)

    cat_var = tk.StringVar()
    tk.Entry(win, textvariable=cat_var).pack(pady=5)

    tk.Button(win, text="Search", command=search).pack(pady=5)



# ------------------------------
# Main GUI
# ------------------------------
root = tk.Tk()
root.title("🧾 Student Expense Tracker by Ankit 545")
root.geometry("400x350")
root.resizable(False, False)

amount_var = tk.StringVar()
category_var = tk.StringVar()
desc_var = tk.StringVar()

tk.Label(root, text="Amount (₹):").pack()
tk.Entry(root, textvariable=amount_var).pack()

tk.Label(root, text="Category:").pack()
tk.Entry(root, textvariable=category_var).pack()

tk.Label(root, text="Description:").pack()
tk.Entry(root, textvariable=desc_var).pack()

tk.Button(root, text="➕ Add Expense", command=add_expense, bg="lightgreen").pack(pady=10)
tk.Button(root, text="📋 View All", command=show_expenses).pack()
tk.Button(root, text="💰 Total Spent", command=show_total).pack()
tk.Button(root, text="🔍 Filter by Category", command=filter_category).pack()

root.mainloop()
