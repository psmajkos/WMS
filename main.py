import mysql.connector
import tkinter as tk
from tkinter import ttk, Frame, NO, IntVar, Radiobutton, SUNKEN, HORIZONTAL, messagebox,Text
from tkcalendar import DateEntry
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
    def expirations():
        query = "SELECT EAN, name, date FROM produkty WHERE date >= CURDATE() - INTERVAL 7 DAY AND date <= CURDATE();"

        try:
            with get_conn() as my_conn:
                with my_conn.cursor() as cursor:
                    cursor.execute("USE warehouse")
                    cursor.execute(query)
                    data = cursor.fetchall()
                    # print(data)
        except mysql.connector.Error as err:
            print(f"Error executing query: {err}")
        finally:
            event = tk.Tk()
            messagebox.showwarning("Message", "Krótka data wazności")
            text_box = Text(
                event,
                height=12,
                width=40
            )
                # Close the cursor (optional, as you will close it when the application exits)
            cursor.close()

            if data is not None:
                text_box.pack(expand=True)
                for row in data:
                    formatted_row = " ".join(str(value) if value is not None else 'None' for value in row)
                    text_box.insert('end', f"{formatted_row}\n")
                    # messagebox.showwarning("Message", "Krótka data wazności")
                text_box.config(state='disabled')
                event.mainloop()
            else:
                pass
        
    expirations()

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

        # my_conn = get_conn()
        # cursor = my_conn.cursor()
        
        # cursor.execute("USE warehouse")


        query = "INSERT INTO produkty(EAN, name, qty, waznosc) VALUES (%s, %s, %s, %s)"
        values = (get_ean, name_get, get_qty, waznosc_get, )
        try:
            with get_conn() as my_conn:
                with my_conn.cursor() as cursor:
                    cursor.execute("USE warehouse")
                    cursor.execute(query, values)
                    my_conn.commit()

        except mysql.connector.Error as err:
            print(f"Error executing query: {err}")
        finally:
            cursor.close()

        # Clear the entry field after inserting the value
        EAN_entry.delete(0, tk.END)
        qty_entry.delete(0, tk.END)
        qty.set(1)
        name_entry.delete(0, tk.END)
        ref()
        actual_mode()
        actual_stock()

    def packing():
        get_ean = EAN.get()
        get_qty = qty.get()
        name_get = name.get()

        # try:
        #     # Reconnect if the connection is lost
        #     my_conn.ping(reconnect=True)
        # except mysql.connector.Error as err:
        #     print(f"Error: {err}")
        #     return
        if get_qty is None:
            get_qty = 1

        query = "INSERT INTO produkty(EAN, name, qty_sell, date) VALUES (%s, %s, %s, %s)"
        values = (get_ean, name_get, get_qty, formatted_date)

        try:
            with get_conn() as my_conn:
                with my_conn.cursor() as cursor:
                    cursor.execute("USE warehouse")
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
        qty.set(1)
        name_entry.delete(0, tk.END)
        ref()
        sell_mode()

    EAN_label = tk.Label(main_frame, text="EAN: ")
    EAN_entry = ttk.Entry(main_frame, textvariable=EAN)
    qty_entry = ttk.Entry(main_frame, textvariable=qty, width=3)
    qty_label = tk.Label(main_frame, text="Qty: ", width=7)
    name_label = tk.Label(main_frame, text="Name: ", width=10)
    name_entry = ttk.Entry(main_frame, textvariable=name)
    waznosc_label = tk.Label(main_frame, text="Ważność", width=10)
    waznosc_entry = DateEntry(main_frame, textvariable=waznosc, date_pattern='y/m/d')
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

    def sell_mode():
        today_table()
        add_button.config(state="disabled")
        send_button.config(state="enabled")   
        waznosc_label.config(text="kiedy")
        root.bind('<Return>', lambda event=None: packing())
        # ref()

    def actual_mode():
        actual_stock()
        waznosc_label.config(text="Ważność")
        send_button.config(state="disabled")
        add_button.config(state="enabled")
        root.bind('<Return>', lambda event=None: add_qty_to_db())
        # ref()

    def overall_mode():
        overall_sent()
        waznosc_label.config(text="kiedy")
        send_button.config(state="enabled")
        add_button.config(state="disabled")
        root.bind('<Return>', lambda event=None: packing())
        # ref()

    def find_by_ean_mode():
        # find_by_ean()
        send_button.config(state="disabled")
        add_button.config(state="enabled")
        search = ttk.Button(root, text="wyszukaj po ean", command=find_by_ean)
        search.grid(row=3,column=2)




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
    actual_radio = Radiobutton(radio_frame, text="Stock",
                        variable=r, value=0,    highlightthickness=0, command=actual_mode)
    actual_radio.grid(column=2, row=6, sticky="W")

    normal = Radiobutton(radio_frame, text="Wysyłka",
                        variable=r, value=1,    highlightthickness=0, command=sell_mode)
    normal.grid(column=2, row=4, sticky="W")

    overall_radio = Radiobutton(radio_frame, text="Wysłane",
                        variable=r, value=2,    highlightthickness=0, command=overall_mode)
    overall_radio.grid(column=2, row=7, sticky="W")

    find_by_ean_radio = Radiobutton(radio_frame, text="znajdz po EAN",
                        variable=r, value=3,    highlightthickness=0, command=find_by_ean_mode)
    find_by_ean_radio.grid(column=2, row=8, sticky="W")


    radio_frame.grid(column=46, row=1)


    operations_frame = Frame(root)
    operations_frame.grid(row=4, column=0)

    operations = ttk.Treeview(operations_frame, height=20)

    operations.column("#0", width=0,  stretch=NO)

    def today_table():
        columns = ('EAN', 'Name', 'Qty Sell', 'Date')
        headings = ('EAN', 'Name', 'Qty Sell', 'Date')

        configure_treeview(columns, headings)
        date = formatted_date
        query = "SELECT EAN, qty_sell, date FROM produkty WHERE date = %s "

        try:
            with get_conn() as my_conn:
                with my_conn.cursor() as cursor:
                    cursor.execute("USE warehouse")
                    cursor.execute(query, (date, ))
                    data = cursor.fetchall()

            # Clear existing items in the Treeview
            for item in operations.get_children():
                operations.delete(item)

            # Insert new data into the Treeview
            for idx, row in enumerate(data, start=1):
                if row[2] is not None:
                    operations.insert(parent='', index='end', iid=str(idx), text='', values=row)
        except mysql.connector.Error as err:
            print(f"Error executing query: {err}")
        finally:
            # Close the cursor
            cursor.close()

    def find_by_ean():
        columns = ('EAN', 'Name','QTY', 'Qty Sell', 'Date')
        headings = ('EAN', 'Name','QTY', 'Qty Sell', 'Date')

        configure_treeview(columns, headings)
        ean_to_compare = EAN.get()
        query = "SELECT EAN, name, qty, qty_sell, waznosc, date FROM produkty WHERE EAN = %s "

        try:
            with get_conn() as my_conn:
                with my_conn.cursor() as cursor:
                    cursor.execute("USE warehouse")
                    cursor.execute(query, (ean_to_compare, ))
                    data = cursor.fetchall()

            # Clear existing items in the Treeview
            for item in operations.get_children():
                operations.delete(item)

            # Insert new data into the Treeview
            for idx, row in enumerate(data, start=1):
                if row[0] is not None:
                    operations.insert(parent='', index='end', iid=str(idx), text='', values=row)
        except mysql.connector.Error as err:
            print(f"Error executing query: {err}")
        finally:
            # Close the cursor
            cursor.close()


    def overall_sent():
        columns = ('EAN', 'Name', 'Qty Sell', 'Date')
        headings = ('EAN', 'Name', 'Qty Sell', 'Date')

        configure_treeview(columns, headings)
        # try:
        #     my_conn.ping(reconnect=True)  # Reconnect if the connection is lost
        # except mysql.connector.Error as err:
        #     print(f"Error: {err}")
        #     return
        # cursor = my_conn.cursor()
        # cursor.execute("USE warehouse")
        date = waznosc.get()

        if date == '':
            query = "SELECT EAN, name, qty_sell, date FROM produkty"
            try:
                with get_conn() as my_conn:
                    with my_conn.cursor() as cursor:
                        cursor.execute("USE warehouse")
                        cursor.execute(query)
                        data = cursor.fetchall()

                # Clear existing items in the Treeview
                for item in operations.get_children():
                    operations.delete(item)

                # Insert new data into the Treeview
                for idx, row in enumerate(data, start=1):
                    if row[2] is not None:
                        operations.insert(parent='', index='end', iid=str(idx), text='', values=row)
                # for row in data:
                #     if row[2] is not None:
                #         operations.insert(parent='', index='end', iid=row[0], text='', values=row)
            except mysql.connector.Error as err:
                print(f"Error executing query: {err}")
            finally:
                # Close the cursor
                cursor.close()
        else:
            query = "SELECT EAN, name, qty_sell, date FROM produkty WHERE date = %s"
            try:
                with get_conn() as my_conn:
                    with my_conn.cursor() as cursor:
                        cursor.execute("USE warehouse")
                        cursor.execute(query, (date, ))
                        data = cursor.fetchall()

                # Clear existing items in the Treeview
                for item in operations.get_children():
                    operations.delete(item)

                # Insert new data into the Treeview
                for idx, row in enumerate(data, start=1):
                    if row[2] is not None:
                        operations.insert(parent='', index='end', iid=str(idx), text='', values=row)
                # for row in data:
                #     if row[2] is not None:
                #         operations.insert(parent='', index='end', iid=row[0], text='', values=row)
            except mysql.connector.Error as err:
                print(f"Error executing query: {err}")
            finally:
                # Close the cursor
                cursor.close()
                

    def copy_ean():
        selected_item = operations.selection()
        if selected_item:
            ean_index = 0  # Assuming EAN is the first column in your Treeview
            ean_value = operations.item(selected_item, 'values')[ean_index]
            root.clipboard_clear()
            root.clipboard_append(ean_value)
            root.update()

    # Create a button for copying EAN
    copy_button = ttk.Button(root, text="Copy EAN", command=copy_ean)
    copy_button.grid(row=2, column=0)  # Adjust the row and column as needed

    def actual_stock():
        columns = ('EAN', "name", 'Qty Difference')
        headings = ('EAN', "name", 'Qty Stock')

        configure_treeview(columns, headings)

        # try:
        #     my_conn.ping(reconnect=True)  # Reconnect if the connection is lost
        # except mysql.connector.Error as err:
        #     print(f"Error: {err}")
        #     return
        # cursor = my_conn.cursor()
        # cursor.execute("USE warehouse")
        query = "SELECT EAN, name, SUM(COALESCE(qty, 0) - COALESCE(qty_sell, 0)) AS qty_difference FROM produkty GROUP BY EAN, name;"


        try:
            with get_conn() as my_conn:
                with my_conn.cursor() as cursor:
                    cursor.execute("USE warehouse")
                    cursor.execute(query)
                    data = cursor.fetchall()

            # Clear existing items in the Treeview
            for item in operations.get_children():
                operations.delete(item)

            # Insert new data into the Treeview
            for idx, row in enumerate(data, start=1):
                # if row[2] is not None:
                if row[2] != 0:
                    operations.insert(parent='', index='end', iid=str(idx), text='', values=row)
            operations.update()

        except mysql.connector.Error as err:
            print(f"Error executing query: {err}")
        finally:
            cursor.close()

    main_frame.grid(row=0)
    operations.pack()
    actual_stock()

    def ref():
        for item in operations.get_children():
            operations.delete(item)

        operations.update()
        operations.pack()  
    root.mainloop()
main()
