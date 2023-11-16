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

cursor.execute("CREATE DATABASE IF NOT EXISTS wms")

cursor.execute("USE wms")


cursor.execute('''CREATE TABLE IF NOT EXISTS products
                (product_id INT AUTO_INCREMENT PRIMARY KEY,
                EAN BIGINT NOT NULL,
                name VARCHAR(45))''')

cursor.execute('''CREATE TABLE IF NOT EXISTS inventory
                (inventory_id INT AUTO_INCREMENT PRIMARY KEY,
                product_id INT,
                quantity INT,
                location VARCHAR(255),
                expiration_date DATE,
                entry_date DATE,
                FOREIGN KEY (product_id) REFERENCES products(product_id))''')

cursor.execute('''CREATE TABLE IF NOT EXISTS transactions
                (id INT AUTO_INCREMENT PRIMARY KEY,
                product_id INT,
                qty INT,
                transaction_date DATE,
                FOREIGN KEY (product_id) REFERENCES products(product_id))''')

def main():
    # def expirations():
    #     query = '''SELECT subquery.EAN, subquery.name, subquery.qty_difference FROM (
    #                     SELECT EAN, name, SUM(COALESCE(qty, 0) - COALESCE(qty_sell, 0)) AS qty_difference
    #                     FROM products
    #                     WHERE waznosc >= CURDATE() - INTERVAL 7 DAY AND waznosc >= CURDATE()
    #                     GROUP BY EAN, name) AS subquery;
    #                 '''
    #     try:
    #         with get_conn() as my_conn:
    #             with my_conn.cursor() as cursor:
    #                 cursor.execute("USE warehouse")
    #                 cursor.execute(query)
    #                 data = cursor.fetchall()
    #                 # print(data)
    #     except mysql.connector.Error as err:
    #         print(f"Error executing query: {err}")
    #     finally:
    #         if data:
    #             event = tk.Tk()
    #             messagebox.showwarning("Message", "Krótka data wazności")
    #             text_box = Text(
    #             event,
    #             height=12,
    #             width=40)
    #             cursor.close()

    #             if data is not None:
    #                 text_box.pack(expand=True)
    #                 for row in data:
    #                     formatted_row = " ".join(str(value) if value is not None else 'None' for value in row)
    #                     text_box.insert('end', f"{formatted_row}\n")
    #                 text_box.config(state='disabled')
    #                 event.mainloop()
    #             else:
    #                 pass
    # expirations()

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
        name_get = name.get()

        query = "INSERT INTO products(EAN, name) VALUES (%s, %s)"
        values = (get_ean, name_get, )
        try:
            with get_conn() as my_conn:
                with my_conn.cursor() as cursor:
                    cursor.execute("USE wms")
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

        if get_qty is None:
            get_qty = 1

        # Assuming 'EAN' corresponds to 'product_id' in the 'products' table
        product_id_query = "SELECT product_id FROM products WHERE EAN = %s"
        product_id_values = (get_ean, )

        try:
            with get_conn() as my_conn:
                with my_conn.cursor() as cursor:
                    cursor.execute("USE wms")
                    cursor.execute(product_id_query, product_id_values)
                    product_id = cursor.fetchone()

                    if product_id:
                        # 'product_id' retrieved from 'products' table
                        query = "INSERT INTO transactions(product_id, qty, transaction_date) VALUES (%s, %s, %s)"
                        values = (product_id[0], get_qty, formatted_date)

                        cursor.execute(query, values)
                        my_conn.commit()
                    else:
                        print("Product not found.")

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
    EAN_entry.focus_set()
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

    def actual_mode():
        actual_stock()
        waznosc_label.config(text="Ważność")
        send_button.config(state="disabled")
        add_button.config(state="enabled")
        root.bind('<Return>', lambda event=None: add_qty_to_db())

    def overall_mode():
        overall_sent()
        waznosc_label.config(text="kiedy")
        send_button.config(state="enabled")
        add_button.config(state="disabled")
        root.bind('<Return>', lambda event=None: packing())

    def find_by_ean_mode():
        send_button.config(state="disabled")
        add_button.config(state="enabled")
        search = ttk.Button(root, text="wyszukaj po ean", command=find_by_ean)
        search.grid(row=3,column=2)

    def total_stock_mode():
        send_button.config(state="disabled")
        add_button.config(state="disabled")
        base_stock()

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

    overall_radio = Radiobutton(radio_frame, text="Wszystkie wysłane",
                        variable=r, value=2,    highlightthickness=0, command=overall_mode)
    overall_radio.grid(column=2, row=7, sticky="W")

    find_by_ean_radio = Radiobutton(radio_frame, text="znajdz po EAN",
                        variable=r, value=3,    highlightthickness=0, command=find_by_ean_mode)
    find_by_ean_radio.grid(column=2, row=8, sticky="W")

    total_stock_radio = Radiobutton(radio_frame, text="wszystkie",
                        variable=r, value=4,    highlightthickness=0, command=total_stock_mode)
    total_stock_radio.grid(column=2, row=9, sticky="W")


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

        query = '''
            SELECT p.EAN, p.name, t.qty, t.transaction_date
            FROM transactions t
            JOIN products p ON t.product_id = p.product_id
            WHERE t.transaction_date = %s
        '''

        try:
            with get_conn() as my_conn:
                with my_conn.cursor() as cursor:
                    cursor.execute("USE wms")
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
        columns = ('EAN', 'Name', 'Quantity', 'Location', 'Expiration Date', 'Transaction Date')
        headings = ('EAN', 'Name', 'Quantity', 'Location', 'Expiration Date', 'Transaction Date')

        configure_treeview(columns, headings)
        ean_to_compare = EAN.get()

        query = '''
            SELECT p.EAN, p.name, i.quantity, i.location, i.expiration_date, t.transaction_date
            FROM products p
            LEFT JOIN inventory i ON p.product_id = i.product_id
            LEFT JOIN transactions t ON p.product_id = t.product_id
            WHERE p.EAN = %s
        '''

        try:
            with get_conn() as my_conn:
                with my_conn.cursor() as cursor:
                    cursor.execute("USE wms")
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

        date = waznosc.get()

        if date == '':
            # query = '''
            #     SELECT p.EAN, p.name, COALESCE(SUM(t.qty), 0) AS qty_sell, t.transaction_date
            #     FROM products p
            #     LEFT JOIN transactions t ON p.product_id = t.product_id
            #     GROUP BY p.EAN, p.name, t.transaction_date;
            # '''

            query = '''
            SELECT p.EAN, p.name, t.qty, t.transaction_date
            FROM transactions t
            JOIN products p ON t.product_id = p.product_id
        '''
            try:
                with get_conn() as my_conn:
                    with my_conn.cursor() as cursor:
                        cursor.execute("USE wms")
                        cursor.execute(query)
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
        else:
            query = '''
                SELECT p.EAN, p.name, COALESCE(SUM(t.qty), 0) AS qty_sell, t.transaction_date
                FROM products p
                LEFT JOIN transactions t ON p.product_id = t.product_id
                WHERE t.transaction_date = %s
                GROUP BY p.EAN, p.name, t.transaction_date;
            '''
            try:
                with get_conn() as my_conn:
                    with my_conn.cursor() as cursor:
                        cursor.execute("USE wms")
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
        columns = ('EAN', "name", 'qty_difference', 'quantity_comparison')
        headings = ('EAN', "name", 'Qty Stock','quantity_comparison')

        configure_treeview(columns, headings)
        
        query = '''
        SELECT 
            p.EAN, 
            p.name,
            COALESCE(i.total_quantity, 0) - COALESCE(SUM(t.qty), 0) AS qty_difference,
            CASE
                WHEN COALESCE(i.total_quantity, 0) = COALESCE(SUM(t.qty), 0) THEN 'Match'
                WHEN COALESCE(i.total_quantity, 0) > COALESCE(SUM(t.qty), 0) THEN 'Inventory Excess'
                WHEN COALESCE(i.total_quantity, 0) < COALESCE(SUM(t.qty), 0) THEN 'Transaction Excess'
                ELSE 'Unknown'
            END AS quantity_comparison
        FROM 
            products p
        LEFT JOIN 
            (
                SELECT product_id, SUM(quantity) AS total_quantity
                FROM inventory
                GROUP BY product_id
            ) i ON p.product_id = i.product_id
        LEFT JOIN 
            transactions t ON p.product_id = t.product_id
        GROUP BY 
            p.EAN, p.name, i.total_quantity;
        '''

        try:
            with get_conn() as my_conn:
                with my_conn.cursor() as cursor:
                    cursor.execute("USE wms")
                    cursor.execute(query)
                    data = cursor.fetchall()

            # Clear existing items in the Treeview
            for item in operations.get_children():
                operations.delete(item)

            # Insert new data into the Treeview
            for idx, row in enumerate(data, start=1):
                if row[2] != 0:
                    operations.insert(parent='', index='end', iid=str(idx), text='', values=row)
            operations.update()

        except mysql.connector.Error as err:
            print(f"Error executing query: {err}")
        finally:
            cursor.close()


    def base_stock():
        date = waznosc.get()
        columns = ('EAN', 'Name', 'Quantity', 'Location', 'Expiration Date', 'Qty Difference', 'Entry Date')
        headings = ('EAN', 'Name', 'Quantity', 'Location', 'Expiration Date', 'Qty Difference', 'Date')

        configure_treeview(columns, headings)

        query = '''
                SELECT
                    p.EAN,
                    p.name,
                    MAX(i.quantity) AS quantity,
                    MAX(i.location) AS location,
                    MAX(i.expiration_date) AS expiration_date,
                    SUM(COALESCE(i.quantity, 0) - COALESCE(t.qty, 0)) AS qty_difference,
                    MAX(i.entry_date) AS entry_date
                FROM
                    products p
                LEFT JOIN
                    inventory i ON p.product_id = i.product_id
                LEFT JOIN
                    transactions t ON p.product_id = t.product_id
                GROUP BY
                    p.EAN, p.name
                '''

        try:
            with get_conn() as my_conn:
                with my_conn.cursor() as cursor:
                    cursor.execute("USE wms")
                    cursor.execute(query)
                    data = cursor.fetchall()

            # Clear existing items in the Treeview
            for item in operations.get_children():
                operations.delete(item)

            # Insert new data into the Treeview
            for idx, row in enumerate(data, start=1):
                if row[2] is not None:
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
