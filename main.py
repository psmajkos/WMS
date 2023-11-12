import mysql.connector
import tkinter as tk
from tkinter import ttk
from datetime import datetime

import datetime

# time = datetime.datetime.now()

# print(time)

# print(time.year, time.month, time.day, time.hour, time.minute)

from datetime import datetime

# Get the current date
current_date = datetime.now()

# Format the date as 'YYYY-MM-DD'
formatted_date = current_date.strftime('%Y-%m-%d')

print(formatted_date)



root = tk.Tk()
root.title("Product Inventory")

EAN = tk.IntVar()
qty = tk.IntVar()

def view():
    pass

def main():

    def insert():
        get_ean = EAN.get()
        get_qty = qty.get()

        query = "INSERT INTO produkty(EAN, qty, date) VALUES (%s, %s, %s)"
        values = (get_ean, get_qty, formatted_date, )

        cursor.execute(query, values)
        my_conn.commit()

        # Clear the entry field after inserting the value
        EAN_entry.delete(0, tk.END)
        qty_entry.delete(0, tk.END)

    def remove():
        get_ean = EAN.get()
        get_qty = qty.get()

        query = "INSERT INTO produkty(EAN, qty_sell, date) VALUES (%s, %s, %s)"
        values = (get_ean, get_qty, formatted_date, )

        cursor.execute(query, values)
        my_conn.commit()

        # Clear the entry field after inserting the value
        EAN_entry.delete(0, tk.END)
        qty_entry.delete(0, tk.END)

    
    EAN_label = tk.Label(root, text="EAN:")
    EAN_label.grid(row=0, column=0)

    EAN_entry = ttk.Entry(root, textvariable=EAN)
    EAN_entry.grid(row=0, column=1)

    qty_entry = ttk.Entry(root, textvariable=qty)
    qty_entry.grid(row=0, column=2)

    add_button = ttk.Button(root, text="Add Product", command=insert)
    add_button.grid(row=1, column=0)

    remove_button = ttk.Button(root, text="Remove Product", command=remove)
    remove_button.grid(row=1, column=1)
main()

def get_conn():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        passwd=""
    )

my_conn = get_conn()
cursor = my_conn.cursor()

cursor.execute("CREATE DATABASE IF NOT EXISTS warehouse")

# Switch to the 'warehouse' database
cursor.execute("USE warehouse")

# Create the 'produkty' table
cursor.execute('''CREATE TABLE IF NOT EXISTS produkty
                (id INT AUTO_INCREMENT PRIMARY KEY,
                EAN INT(45) NOT NULL,
                name VARCHAR(45),
                qty INT(100),
                qty_sell INT(100),
                date DATE)''')

root.mainloop()
