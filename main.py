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
                date DATE,
                waznosc DATE)''')

def main():

    def refresh():
        for item in operations.get_children():
            operations.delete(item)

    
    def configure_treeview(columns, headings):
        # Remove existing columns
        for col in operations['columns']:
            operations.heading(col, text="")

        # Configure new columns
        operations['columns'] = columns
        for col, heading in zip(columns, headings):
            operations.heading(col, text=heading)

    # Get the current date
    current_date = datetime.now()

    # Format the date as 'YYYY-MM-DD'
    formatted_date = current_date.strftime('%Y-%m-%d')

    # print(formatted_date)

    root = tk.Tk()
    root.title("Product Inventory")

    main_frame = tk.Frame(root)

    EAN = tk.IntVar()
    EAN.set("")
    qty = tk.IntVar()
    qty.set(1)
    name = tk.StringVar()
    waznosc = tk.StringVar()


    def add_qty_to_db():
        get_ean = EAN.get()
        get_qty = qty.get()
        name_get = name.get()
        waznosc_get = waznosc.get()

        
        my_conn = get_conn()
        cursor = my_conn.cursor()
        cursor.execute("USE warehouse")

        query = "INSERT INTO produkty(EAN, name, qty, waznosc) VALUES (%s, %s, %s, %s)"
        values = (get_ean, name_get, get_qty, waznosc_get, )
        print(waznosc_get)

        cursor.execute(query, values)
        my_conn.commit()

        # Clear the entry field after inserting the value
        EAN_entry.delete(0, tk.END)
        qty_entry.delete(0, tk.END)
        name_entry.delete(0, tk.END)
        waznosc_entry.delete(0, tk.END)

    def packing():
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

    EAN_label = tk.Label(main_frame, text="EAN: ")
    EAN_entry = ttk.Entry(main_frame, textvariable=EAN)
    qty_entry = ttk.Entry(main_frame, textvariable=qty, width=3)
    qty_label = tk.Label(main_frame, text="Qty: ")
    name_label = tk.Label(main_frame, text="Name: ")
    name_entry = ttk.Entry(main_frame, textvariable=name)
    waznosc_label = tk.Label(main_frame, text="Waznosc")
    waznosc_entry = ttk.Entry(main_frame, textvariable=waznosc)
    add_button = ttk.Button(main_frame, text="Dodaj do bazy", command=add_qty_to_db)
    send_button = ttk.Button(main_frame, text="Nadaj", command=packing)

    EAN_label.grid(row=0, column=0)
    EAN_entry.grid(row=0, column=1)
    EAN_entry.focus()
    qty_label.grid(row=0, column=2)
    qty_entry.grid(row=0, column=3)
    name_label.grid(row=0, column=4)
    name_entry.grid(row=0, column=5)
    waznosc_label.grid(row=0, column=6)
    waznosc_entry.grid(row=0, column=7)
    add_button.grid(row=1, column=0)
    send_button.grid(row=1, column=1)
    # btn = ttk.Button(root, command=refresh)
    # btn.grid(row=6, column=4)

    def sell_mode():
        today_table()
        add_button.config(state="disabled")
        send_button.config(state="enabled")
        # refresh()
        

    def insert_mode():
        insert_to_db()
        send_button.config(state="disabled")
        add_button.config(state="enabled")
        # refresh()

    def qty_mode():
        qty_only()
        send_button.config(state="disabled")
        add_button.config(state="enabled")

    def actual_mode():
        actual_stock()


    radio_frame = tk.Frame(main_frame, bd=2, relief=SUNKEN)

    mode_of_transportation = ttk.Label(radio_frame, text="Model pracy: ")
    mode_of_transportation.grid(column=2, row=1)


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

    qty_radio = Radiobutton(radio_frame, text="qty only",
                        variable=r, value=2,    highlightthickness=0, command=qty_mode)
    qty_radio.grid(column=2, row=5, sticky="W")

    actual_radio = Radiobutton(radio_frame, text="actual only",
                        variable=r, value=3,    highlightthickness=0, command=actual_mode)
    actual_radio.grid(column=2, row=6, sticky="W")

    radio_frame.grid(column=46, row=1)

    main_frame.grid(row=0)

    btn = ttk.Button(root, command=refresh)
    btn.grid(row=6, column=4)

    operations_frame = Frame(root)
    operations_frame.grid(row=4, column=0)

    operations = ttk.Treeview(operations_frame, height=20)

    operations['columns'] = ('EAN', 'Name', 'QTY_SELL', 'Date')

    operations.column("#0", width=0,  stretch=NO)
    operations.column("EAN",anchor=CENTER, width=160)
    operations.column("Name",anchor=CENTER,width=160)
    # operations.column("QTY",anchor=CENTER,width=80)
    operations.column("QTY_SELL",anchor=CENTER,width=80)
    operations.column("Date",anchor=CENTER,width=100)

    operations.heading("#0",text="",anchor=CENTER)
    operations.heading("EAN",text="EAN",anchor=CENTER)
    operations.heading("Name",text="Name",anchor=CENTER)
    # operations.heading("QTY",text="Qty",anchor=CENTER)
    operations.heading("QTY_SELL",text="Qty sell",anchor=CENTER)
    operations.heading("Date",text="Date",anchor=CENTER)

    def qty_only():
        columns = ('EAN', 'Total Quantity')
        headings = ('EAN', 'Total Quantity')

        configure_treeview(columns, headings)
        try:
            my_conn.ping(reconnect=True)  # Reconnect if the connection is lost
        except mysql.connector.Error as err:
            print(f"Error: {err}")
            return
        
        cursor = my_conn.cursor()

        try:
            cursor.execute("USE warehouse")
            # query = "SELECT EAN, name, qty, waznosc, date FROM produkty"
            query = "SELECT EAN, SUM(qty) AS total_quantity FROM produkty GROUP BY EAN"
            cursor.execute(query)
            data = cursor.fetchall()

            # Clear existing items in the Treeview
            for item in operations.get_children():
                operations.delete(item)

            # Insert new data into the Treeview
            for index, row in enumerate(data, start=1):
                operations.insert(parent='', index='end', iid=index, text='', values=row)
                    # print(row)  # Print each row to check if data is fetched correctly
        except mysql.connector.Error as err:
            print(f"Error executing query: {err}")
        finally:
            # Close the cursor
            cursor.close()


    def insert_to_db():
        columns = ('EAN', 'Total Quantity', 'Waznosc')
        headings = ('EAN', 'Total Quantity', 'Waznosc')

        configure_treeview(columns, headings)
        try:
            my_conn.ping(reconnect=True)  # Reconnect if the connection is lost
        except mysql.connector.Error as err:
            print(f"Error: {err}")
            return
        cursor = my_conn.cursor()

        try:
            cursor.execute("USE warehouse")
            # query = "SELECT EAN, name, qty, waznosc, date FROM produkty"
            query = "SELECT EAN, SUM(qty) AS total_quantity, waznosc FROM produkty GROUP BY EAN, waznosc"
            cursor.execute(query)
            data = cursor.fetchall()

            # Clear existing items in the Treeview
            for item in operations.get_children():
                operations.delete(item)

            # Insert new data into the Treeview
            for index, row in enumerate(data, start=1):
                operations.insert(parent='', index='end', iid=index, text='', values=row)
                    # print(row)  # Print each row to check if data is fetched correctly
        except mysql.connector.Error as err:
            print(f"Error executing query: {err}")
        finally:
            # Close the cursor
            cursor.close()


    def today_table():
        columns = ('EAN', 'Name', 'Qty Sell', 'Date')
        headings = ('EAN', 'Name', 'Qty Sell', 'Date')

        configure_treeview(columns, headings)
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

    def actual_stock():
        columns = ('EAN', 'Qty Difference')
        headings = ('EAN', 'Qty Difference')

        configure_treeview(columns, headings)

        try:
            my_conn.ping(reconnect=True)  # Reconnect if the connection is lost
        except mysql.connector.Error as err:
            print(f"Error: {err}")
            return
        cursor = my_conn.cursor()
        cursor.execute("USE warehouse")
        date = formatted_date
        query = "SELECT EAN, SUM(coalesce(qty, 0) - coalesce(qty_sell, 0)) AS qty_difference FROM produkty GROUP BY EAN"

        try:
            cursor.execute(query, (date, ))
            data = cursor.fetchall()


            # Clear existing items in the Treeview
            for item in operations.get_children():
                operations.delete(item)

            # Insert new data into the Treeview
            for row in data:
                print(row)
                if row[2] is not None:
                    operations.insert(parent='', index='end', iid=row[0], text='', values=row)
                print(row)  # Print each row to check if data is fetched correctly
        except mysql.connector.Error as err:
            print(f"Error executing query: {err}")
        finally:
            # Close the cursor
            cursor.close()

    operations.pack()

    insert_to_db()
    

    root.mainloop()
main()
# restart main? 