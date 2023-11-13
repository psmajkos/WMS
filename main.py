import mysql.connector
import tkinter as tk
from tkinter import ttk, Frame, CENTER, NO
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

def get_conn():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        passwd="Pcf85830"
    )

my_conn = get_conn()
cursor = my_conn.cursor()

cursor.execute("CREATE DATABASE IF NOT EXISTS warehouse")

# Switch to the 'warehouse' database
cursor.execute("USE warehouse")



# Create the 'produkty' table
cursor.execute('''CREATE TABLE IF NOT EXISTS produkty
                (id INT AUTO_INCREMENT PRIMARY KEY,
                EAN BIGINT NOT NULL,
                name VARCHAR(45),
                qty INT(100),
                qty_sell INT(100),
                date DATE)''')



root = tk.Tk()
root.title("Product Inventory")

EAN = tk.IntVar()
EAN.set("")
qty = tk.IntVar()
qty.set("")

def view():
    pass

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

def view_products():
    query = "SELECT EAN, name, qty, qty_sell, date FROM produkty"

    cursor.execute(query)

    data = cursor.fetchall()

    # for row in data:
    #     print(data)

    # my_conn.close()
view_products()

operations_frame = Frame(root)
operations_frame.grid(row=4, column=0)

operations = ttk.Treeview(operations_frame)

operations['columns'] = ('EAN', 'Name', 'QTY', 'QTY_SELL', 'Date')

operations.column("#0", width=0,  stretch=NO)
operations.column("EAN",anchor=CENTER, width=80)
operations.column("Name",anchor=CENTER,width=80)
operations.column("QTY",anchor=CENTER,width=80)
operations.column("QTY_SELL",anchor=CENTER,width=80)
operations.column("Date",anchor=CENTER,width=80)

operations.heading("#0",text="",anchor=CENTER)
operations.heading("EAN",text="EAN",anchor=CENTER)
operations.heading("Name",text="Name",anchor=CENTER)
operations.heading("QTY",text="Qty",anchor=CENTER)
operations.heading("QTY_SELL",text="Qty sell",anchor=CENTER)
operations.heading("Date",text="Date",anchor=CENTER)


def fetch_and_display_data():
    try:
        my_conn.ping(reconnect=True)  # Reconnect if the connection is lost
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return
    cursor.execute("USE warehouse")
    query = "SELECT EAN, name, qty, qty_sell, date FROM produkty"

    try:
        cursor.execute(query)
        data = cursor.fetchall()

        # Clear existing items in the Treeview
        for item in operations.get_children():
            operations.delete(item)

        # Insert new data into the Treeview
        for row in data:
            operations.insert(parent='', index='end', iid=row[0], text='', values=row)
            print(row)  # Print each row to check if data is fetched correctly
    except mysql.connector.Error as err:
        print(f"Error executing query: {err}")
    finally:
        # Close the cursor
        cursor.close()

# Call the function to fetch and display data when the program starts
fetch_and_display_data()

operations.pack()

root.mainloop()
