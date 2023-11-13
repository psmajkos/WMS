import mysql.connector
import tkinter as tk
from tkinter import ttk, Frame, CENTER, NO, IntVar, Radiobutton, SUNKEN, HORIZONTAL, X
from datetime import datetime

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

def main():

    # Get the current date
    current_date = datetime.now()

    # Format the date as 'YYYY-MM-DD'
    formatted_date = current_date.strftime('%Y-%m-%d')

    print(formatted_date)

    root = tk.Tk()
    root.title("Product Inventory")

    main_frame = tk.Frame(root)

    EAN = tk.IntVar()
    EAN.set("")
    qty = tk.IntVar()
    qty.set(1)
    name = tk.StringVar()


    def insert():
        get_ean = EAN.get()
        get_qty = qty.get()
        name_get = name.get()

        
        my_conn = get_conn()
        cursor = my_conn.cursor()
        cursor.execute("USE warehouse")

        query = "INSERT INTO produkty(EAN, name, qty, date) VALUES (%s, %s, %s, %s)"
        values = (get_ean, name_get, get_qty, formatted_date, )

        cursor.execute(query, values)
        my_conn.commit()

        # Clear the entry field after inserting the value
        EAN_entry.delete(0, tk.END)
        qty_entry.delete(0, tk.END)
        name_entry.delete(0, tk.END)

        # operations_frame.destroy()
        # operations_frame()
        
    def remove():
        global cursor  # Declare cursor as a global variable

        get_ean = EAN.get()
        get_qty = qty.get()

        try:
            # Reconnect if the connection is lost
            my_conn.ping(reconnect=True)
        except mysql.connector.Error as err:
            print(f"Error: {err}")
            return
        if get_qty is None:
            get_qty = 1

        query = "INSERT INTO produkty(EAN, qty_sell, date) VALUES (%s, %s, %s)"
        values = (get_ean, get_qty, formatted_date)

        try:
            cursor = my_conn.cursor()  # Reopen the cursor
            cursor.execute(query, values)
            my_conn.commit()
        except mysql.connector.Error as err:
            print(f"Error executing query: {err}")
        finally:
            # Close the cursor (optional, as you will close it when the application exits)
            cursor.close()

        # Clear the entry field after inserting the value
        EAN_entry.delete(0, tk.END)
        qty_entry.delete(0, tk.END)
        name_entry.delete(0, tk.END)
        # operations_frame.destroy()
        # operations_frame()

    EAN_label = tk.Label(main_frame, text="EAN: ")
    EAN_entry = ttk.Entry(main_frame, textvariable=EAN)
    qty_entry = ttk.Entry(main_frame, textvariable=qty, width=3)
    qty_label = tk.Label(main_frame, text="Qty: ")
    name_label = tk.Label(main_frame, text="Name: ")
    name_entry = ttk.Entry(main_frame, textvariable=name)
    add_button = ttk.Button(main_frame, text="Dodaj do bazy", command=insert)
    remove_button = ttk.Button(main_frame, text="Nadaj", command=remove)

    EAN_label.grid(row=0, column=0)
    EAN_entry.grid(row=0, column=1)
    qty_label.grid(row=0, column=2)
    qty_entry.grid(row=0, column=3)
    name_label.grid(row=0, column=4)
    name_entry.grid(row=0, column=5)
    add_button.grid(row=1, column=0)
    remove_button.grid(row=1, column=1)

    def sell_mode():
        today_table()
        add_button.config(state="disabled")
        remove_button.config(state="enabled")
        

    def insert_mode():
        insert_to_db()
        remove_button.config(state="disabled")
        add_button.config(state="enabled")

    radio_frame = tk.Frame(main_frame, bd=2, relief=SUNKEN)

    mode_of_transportation = ttk.Label(radio_frame, text="Model pracy: ")
    mode_of_transportation.grid(column=2, row=1)

    # separator = ttk.Separator(radio_frame, orient='horizontal')
    # separator.pack(fill='x')
# horizontal separator
    ttk.Separator(
        master=radio_frame,
        orient=HORIZONTAL,
        style='blue.TSeparator',
        class_= ttk.Separator,
        takefocus= 1,
        cursor='plus'    
    ).grid(row=2, column=3, ipadx=0, pady=10)
        
    r = IntVar()
    express = Radiobutton(radio_frame, text="Dodaj do bazy",
                        variable=r, value=0, highlightthickness=0, command=insert_mode)
    express.grid(column=2, row=3, sticky="W")

    normal = Radiobutton(radio_frame, text="Wysyłka",
                        variable=r, value=1,    highlightthickness=0, command=sell_mode)
    normal.grid(column=2, row=4, sticky="W")

    radio_frame.grid(column=46, row=1)

    main_frame.grid(row=0)


    operations_frame = Frame(root)
    operations_frame.grid(row=4, column=0)

    operations = ttk.Treeview(operations_frame)

    operations['columns'] = ('EAN', 'Name', 'QTY_SELL', 'Date')

    operations.column("#0", width=0,  stretch=NO)
    operations.column("EAN",anchor=CENTER, width=160)
    operations.column("Name",anchor=CENTER,width=80)
    # operations.column("QTY",anchor=CENTER,width=80)
    operations.column("QTY_SELL",anchor=CENTER,width=80)
    operations.column("Date",anchor=CENTER,width=80)

    operations.heading("#0",text="",anchor=CENTER)
    operations.heading("EAN",text="EAN",anchor=CENTER)
    operations.heading("Name",text="Name",anchor=CENTER)
    # operations.heading("QTY",text="Qty",anchor=CENTER)
    operations.heading("QTY_SELL",text="Qty sell",anchor=CENTER)
    operations.heading("Date",text="Date",anchor=CENTER)

    def insert_to_db():
        try:
            my_conn.ping(reconnect=True)  # Reconnect if the connection is lost
        except mysql.connector.Error as err:
            print(f"Error: {err}")
            return
        cursor = my_conn.cursor()

        try:
            cursor.execute("USE warehouse")
            query = "SELECT EAN, name, qty, qty_sell, date FROM produkty"
            cursor.execute(query)
            data = cursor.fetchall()

            # Clear existing items in the Treeview
            for item in operations.get_children():
                operations.delete(item)

            # Insert new data into the Treeview
            for row in data:
                operations.insert(parent='', index='end', iid=row[0], text='', values=row)
                    # print(row)  # Print each row to check if data is fetched correctly
        except mysql.connector.Error as err:
            print(f"Error executing query: {err}")
        finally:
            # Close the cursor
            cursor.close()


    def today_table():
        try:
            my_conn.ping(reconnect=True)  # Reconnect if the connection is lost
        except mysql.connector.Error as err:
            print(f"Error: {err}")
            return
        cursor = my_conn.cursor()
        cursor.execute("USE warehouse")
        date = formatted_date
        query = "SELECT EAN, name, qty_sell, date FROM produkty WHERE date = %s "

        try:
            cursor.execute(query, (date, ))
            data = cursor.fetchall()

            # Clear existing items in the Treeview
            for item in operations.get_children():
                operations.delete(item)

            # Insert new data into the Treeview
            for row in data:
                if row[2] is not None:
                    operations.insert(parent='', index='end', iid=row[0], text='', values=row)
                print(row)  # Print each row to check if data is fetched correctly
        except mysql.connector.Error as err:
            print(f"Error executing query: {err}")
        finally:
            # Close the cursor
            cursor.close()

    operations.pack()

    root.mainloop()
main()