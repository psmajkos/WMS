import mysql.connector
import tkinter as tk
from tkinter import ttk, Frame, NO, YES, IntVar, Radiobutton, SUNKEN, HORIZONTAL, messagebox,Text, Checkbutton, LEFT
from tkcalendar import DateEntry
from datetime import datetime
import babel.numbers
import json
from ttkwidgets.autocomplete import AutocompleteEntry
from db_connector import get_conn

my_conn = get_conn()
cursor = my_conn.cursor()

cursor.execute("CREATE DATABASE IF NOT EXISTS wms")

cursor.execute("USE wms")

cursor.execute('''CREATE TABLE IF NOT EXISTS products
                (product_id INT AUTO_INCREMENT PRIMARY KEY,
                EAN BIGINT NOT NULL,
                name VARCHAR(80),
                category VARCHAR(80))''')

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

    # Read categories from JSON file
    with open('categories.json', 'r') as file:
        categories_data = json.load(file)
        categories = categories_data.get('categories', [])

    # Get the current date
    current_date = datetime.now()

    # Format the date as 'YYYY-MM-DD'
    formatted_date = current_date.strftime('%Y-%m-%d')

    def configure_treeview(columns, headings):
        # Remove existing columns
        for col in operations['columns']:
            operations.heading(col, text="")

        # Configure new columns
        operations['columns'] = columns
        for col, heading in zip(columns, headings):
            operations.heading(col, text=heading)
            operations.column(col, stretch=tk.YES)

    root = tk.Tk()
    root.title("PANSEN Warehouse Management System")

    # Set geometry to cover the whole screen
    root.geometry("{0}x{1}+0+0".format(root.winfo_screenwidth(), root.winfo_screenheight()))

    # Allow the window to be resizable
    root.resizable(True, True)

    name = tk.StringVar()
    waznosc = tk.StringVar()
    location_var = tk.StringVar()
    category_var = tk.StringVar()
    ean = tk.IntVar()
    qty = tk.IntVar()
    include_expiration_var = IntVar()

    include_expiration_var.set(1)
    ean.set("")
    qty.set(1)

    def add_product():
        """
        Adds a new product to the 'products' table in the database.
        Checks for existing EAN and prompts an error if the EAN already exists.
        """

        get_ean = ean.get()
        name_get = name.get()

        # Check if the EAN and name are not empty
        if not get_ean:
            messagebox.showerror("Błąd", "EAN i nazwa są wymagane!")
            return
        
        # Check if the EAN already exists
        ean_exists_query = "SELECT COUNT(EAN) FROM products WHERE EAN = %s"
        ean_exists_values = (get_ean, )

        try:
            with get_conn() as my_conn:
                with my_conn.cursor() as cursor:
                    cursor.execute("USE wms")
                    cursor.execute(ean_exists_query, ean_exists_values)
                    ean_count = cursor.fetchone()[0]

                    if ean_count > 0:
                        messagebox.showerror("Błąd", "EAN już istnieje!")
                        return

        except mysql.connector.Error as err:
            print(f"Error executing query: {err}")
            return
        finally:
            cursor.close()

        # If EAN doesn't exist, proceed with the insertion
        insert_query = "INSERT INTO products(EAN, name) VALUES (%s, %s)"
        insert_values = (get_ean, name_get)

        try:
            with get_conn() as my_conn:
                with my_conn.cursor() as cursor:
                    cursor.execute("USE wms")
                    cursor.execute(insert_query, insert_values)
                    my_conn.commit()

        except mysql.connector.Error as err:
            print(f"Error executing query: {err}")
            return
        finally:
            cursor.close()

        root.bind('<Return>',lambda event:add_product())

        # Clear the entry field after inserting the value
        ean_entry.delete(0, tk.END)
        name_entry.delete(0, tk.END)
        qty.set(1)
        ref()

    def put_product_to_inventory(include_expiration=True):
        """
        Adds a new product to the 'products' table and puts a product batch in the 'inventory' table in the database.
        Checks for existing EAN, increments quantity if EAN already exists, and inserts the product batch.
        """

        get_ean = ean.get()
        name_get = name.get()
        get_qty = qty.get()
        location = location_var.get()

        if get_qty is None:
            get_qty = 1

        # Check if the EAN and name are not empty
        if not get_ean or not get_qty:
            messagebox.showerror("Błąd!", "EAN i Ilość są wymagane!")
            return

        product_id_query = "SELECT product_id FROM products WHERE EAN = %s"
        product_id_values = (get_ean, )

        try:
            with get_conn() as my_conn:
                with my_conn.cursor() as cursor:
                    cursor.execute("USE wms")
                    
                    # Check if the EAN already exists
                    ean_exists_query = "SELECT COUNT(EAN) FROM products WHERE EAN = %s"
                    ean_exists_values = (get_ean, )
                    cursor.execute(ean_exists_query, ean_exists_values)
                    ean_count = cursor.fetchone()[0]

                    if ean_count > 0:
                        # If EAN exists, increment quantity
                        update_qty_query = "UPDATE inventory SET quantity = quantity + %s WHERE product_id = (SELECT product_id FROM products WHERE EAN = %s)"
                        update_qty_values = (get_qty, get_ean)
                        cursor.execute(update_qty_query, update_qty_values)
                    else:
                        # If EAN doesn't exist, proceed with the insertion
                        insert_product_query = "INSERT INTO products(EAN, name) VALUES (%s, %s)"
                        insert_product_values = (get_ean, name_get)
                        cursor.execute(insert_product_query, insert_product_values)

                        # Retrieve product_id
                        cursor.execute(product_id_query, product_id_values)
                        product_id = cursor.fetchone()

                        if product_id:
                            # Insert product batch with expiration date
                            if include_expiration:
                                query = "INSERT INTO inventory(product_id, quantity, location, expiration_date, entry_date) VALUES (%s, %s, %s, %s, %s)"
                                values = (product_id[0], get_qty, location, waznosc.get(), formatted_date)
                            # Insert product batch without expiration date
                            else:
                                query = "INSERT INTO inventory(product_id, quantity, location, entry_date) VALUES (%s, %s, %s, %s)"
                                values = (product_id[0], get_qty, location, formatted_date)

                            cursor.execute(query, values)
                        else:
                            print("Produktu nie znaleziono.")

                    my_conn.commit()

        except mysql.connector.Error as err:
            print(f"Error executing query: {err}")
        finally:
            cursor.close()

        # Clear the entry fields after inserting the values
        ean_entry.delete(0, tk.END)
        qty_entry.delete(0, tk.END)
        name_entry.delete(0, tk.END)
        qty.set(1)
        ref()
        actual_stock()

    def packing():
        """
        Records a transaction for packing a product.
        Checks for an existing product, retrieves its product_id, and records the transaction.
        """
        get_ean = ean.get()
        get_qty = qty.get()

        if get_qty is None:
            get_qty = 1

        # Check if the EAN and name are not empty
        if not get_ean:
            messagebox.showerror("Błąd", "EAN jest wymagany!")
            return

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
                        print("Produktu nie znaleziono.")

        except mysql.connector.Error as err:
            print(f"Error executing query: {err}")
        finally:
            cursor.close()

        # Clear the entry field after inserting the value
        ean_entry.delete(0, tk.END)
        qty_entry.delete(0, tk.END)
        qty.set(1)
        name_entry.delete(0, tk.END)
        ref()
        sent_today_mode()

    # Function to handle the checkbutton state change
    def handle_expiration_check():
        include_expiration = include_expiration_var.get()
        if include_expiration:
            put_into_inventory_button.config(command=lambda: put_product_to_inventory())
        else:
            put_into_inventory_button.config(command=lambda: put_product_to_inventory(include_expiration=False))

    # Create a frame for the upper part of the GUI
    upper_gui = tk.Frame(root, width=1320, height=500, bd=2, relief=SUNKEN)

    # Create the Checkbutton for expiration date 
    expiration_checkbutton = Checkbutton(upper_gui, text="Z datą ważności", variable=include_expiration_var)

    # Attach the function to the checkbutton state change
    expiration_checkbutton.config(command=handle_expiration_check)

    # Labels and Entry widgets for EAN, Quantity, Name, Expiration Date, Category, and Location
    ean_label = tk.Label(upper_gui, text="EAN: ")
    ean_entry = ttk.Entry(upper_gui, textvariable=ean)
    qty_entry = ttk.Entry(upper_gui, textvariable=qty, width=3)
    qty_label = tk.Label(upper_gui, text="Ilość: ", width=7)
    name_label = tk.Label(upper_gui, text="Nazwa: ", width=10)
    name_entry = ttk.Entry(upper_gui, textvariable=name, width=40)
    exp_label = tk.Label(upper_gui, text="Ważność", width=10)
    exp_entry = DateEntry(upper_gui, textvariable=waznosc, date_pattern='y/m/d')
    category_label = tk.Label(upper_gui, text="(Opcjonalne) Kategoria: ")
    category_combo = ttk.Combobox(upper_gui, text="Kategoria", textvariable=category_var)
    category_combo['values'] = categories
    
    send_button = ttk.Button(upper_gui, text="Nadaj", command=packing)
    location_label = ttk.Label(upper_gui, text="Lokalizacja")
    location_combo = ttk.Combobox(upper_gui, text="Lokalizacja", textvariable=location_var)
    # location_combo['values'] = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H',]
    add_button = ttk.Button(upper_gui, text="Dodaj do bazy", command=add_product)
    

    # Add a button for putting data into inventory
    put_into_inventory_button = ttk.Button(upper_gui, text="Dodaj partie", command=put_product_to_inventory)
    put_into_inventory_button.pack()

    ean_label.pack()
    ean_entry.pack()
    ean_entry.focus_set()
    name_label.pack()
    name_entry.pack()
    qty_label.pack()
    qty_entry.pack()

    exp_label.pack()
    exp_entry.pack()

    send_button.pack()
    location_label.pack()
    location_combo.pack()
    category_label.pack()
    category_combo.pack()
    add_button.pack()
    expiration_checkbutton.pack()

    # Functions for showing and hiding widgets based on different modes
    def show_widgets(widgets):
        for widget in widgets:
            widget.pack()

    def hide_widgets(widgets):
        for widget in widgets:
            widget.pack_forget()
    
    # Mode-specific functions and their associated widgets
    def add_product_mode_widgets():
        show_widgets([name_label, name_entry, ean_label, ean_entry, category_combo, add_button])
        hide_widgets([exp_entry, exp_label, qty_entry, qty_label, location_combo, location_label, copy_button, send_button, put_into_inventory_button, expiration_checkbutton, category_combo, category_label])

    def actual_mode_widgets():
        show_widgets([name_label, name_entry, qty_label, qty_entry, exp_label, exp_entry, location_label, location_combo, copy_button, expiration_checkbutton,category_combo, put_into_inventory_button])
        hide_widgets([send_button, add_button])

    def sent_today_widgets():
        show_widgets([send_button, copy_button, ean_label, ean_entry])
        hide_widgets([add_button, exp_label, exp_entry, qty_label, qty_entry, location_label, location_combo, put_into_inventory_button, name_entry, name_label, expiration_checkbutton, category_combo, category_label])

    def overall_mode_widgets():
        show_widgets([send_button, exp_label, exp_entry])
        hide_widgets([add_button, exp_entry, exp_label, qty_entry, qty_label, location_combo, location_label, copy_button, put_into_inventory_button, expiration_checkbutton, category_combo, category_label])

    def find_by_ean_mode_widgets():
        show_widgets([copy_button, ean_label, ean_entry])
        hide_widgets([name_entry, name_label, exp_entry, exp_label, qty_entry, qty_label, location_combo, location_label, send_button, put_into_inventory_button, add_button, expiration_checkbutton, category_combo, category_label])

    def total_stock_mode_widgets():
        show_widgets([copy_button, exp_label, exp_entry])
        hide_widgets([ean_entry, ean_label, name_entry, name_label ,add_button, qty_entry, qty_label, location_combo, location_label, copy_button, send_button, put_into_inventory_button,expiration_checkbutton, category_combo, category_label])

    def show_eveything_widgets():
        hide_widgets([copy_button, exp_label, exp_entry, ean_entry, ean_label, name_entry, name_label ,add_button, qty_entry, qty_label, location_combo, location_label, copy_button, send_button, put_into_inventory_button,expiration_checkbutton, category_combo, category_label])
    
    def sent_today_mode():
        sent_today_widgets()
        sent_today_table()

    def realtime_stock_mode():
        actual_mode_widgets()
        actual_stock()

    def add_product_mode():
        add_product_mode_widgets()

    def overall_mode():
        overall_mode_widgets()
        overall_sent()

    def find_by_ean_mode():
        find_by_ean_mode_widgets()
        find_by_ean()

    def total_stock_mode():
        total_stock_mode_widgets()
        base_stock()

    def show_eveything_mode():
        show_eveything_widgets()
        show_eveything()

    def expiration_mode():
        display_expirations()

    def copy_ean_from_list():
        selected_item = operations.selection()
        if selected_item:
            ean_index = 0  # Assuming EAN is the first column in your Treeview
            ean_value = operations.item(selected_item, 'values')[ean_index]
            root.clipboard_clear()
            root.clipboard_append(ean_value)
            root.update()

    def edit_row():
        selected_item = operations.selection()
        item_values = operations.item(selected_item, 'values')
        print("Item values:", item_values)

        if selected_item and len(item_values) >= 4:  # Assuming you have at least 4 columns
            ean_value = item_values[0]
            name_ = item_values[1]
            quantity = item_values[2]
            location = item_values[3]

            try:
                with get_conn() as my_conn:
                    with my_conn.cursor() as cursor:
                        cursor.execute("USE wms")

                        # Retrieve product_id based on EAN
                        product_id_query = "SELECT product_id FROM products WHERE EAN = %s"
                        product_id_values = (ean_value, )
                        cursor.execute(product_id_query, product_id_values)
                        product_id = cursor.fetchone()

                        if product_id:
                            # Update inventory based on product_id
                            query = """UPDATE inventory 
                                    SET quantity = %s, location = %s, expiration_date = %s
                                    WHERE product_id = %s;"""
                            values = (qty.get(),location_var.get(), waznosc.get(), product_id[0])

                            cursor.execute(query, values)
                            my_conn.commit()
                            print("Row updated successfully.")
                        else:
                            print("Product not found.")

            except mysql.connector.Error as err:
                print(f"Error executing query: {err}")
            finally:
                cursor.close()
        else:
            print("Not enough values in the tuple.")

    menu = tk.Frame(root, width=400)

    def on_item_click(event):
        selected_items = tree_menu.selection()
        if selected_items:
            item = selected_items[0]
            if item == "item1":
                realtime_stock_mode()
            elif item == "item2":
                find_by_ean_mode()
            elif item == "item3":
                sent_today_mode()
            elif item == "item4":
                expiration_mode()
            elif item == "item5":
                show_eveything_mode()
            elif item == "item6":
                overall_mode()

    tree_menu = ttk.Treeview(menu)
    tree_menu.heading("#0", text="Opcje")
    tree_menu.insert("", "0", "item1", text="Aktualny Stan")
    tree_menu.insert("", "1", "item2", text="Znajdź po EAN")
    tree_menu.insert("", "2", "item3", text="Wysyłka")
    tree_menu.insert("", "3", "item4", text="Krótka data")
    tree_menu.insert("", "4", "item5", text="Wszystko")
    tree_menu.insert("", "5", "item6", text="Wszystkie wysłane")

    tree_menu.bind("<Button-1>", on_item_click)

    # tree_menu.column("#0", width=150, stretch=YES)  # Adjust the width as needed

    tree_menu.pack_propagate(False)

    tree_menu.pack(side=LEFT, fill=tk.BOTH)

    # Create a button for copying EAN
    copy_button = ttk.Button(tree_menu, text="Kopiuj EAN", command=copy_ean_from_list)
    copy_button.pack(side='bottom')

    # # Create a button for copying EAN
    edit_button = ttk.Button(tree_menu, text="Edytuj", command=edit_row)
    edit_button.pack(side='bottom')

    menu.pack(side=LEFT, fill=tk.BOTH)

    operations_frame = Frame(root, bd=2, width=1320, height=400, relief=SUNKEN) 
    operations_frame.pack(side='bottom')
    operations_frame.pack_propagate(False)

    operations = ttk.Treeview(operations_frame, height=20)

    operations.column("#0", width=0,  stretch=NO)

    def sent_today_table():
        columns = ('EAN', 'Name', 'Qty Sell', 'Date')
        headings = ('EAN', 'Nazwa', 'Wysłane', 'Data')

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
            cursor.close()

    def find_by_ean():
        columns = ('EAN', 'Name', 'Quantity', 'Location', 'Expiration Date', 'Entry Date')
        headings = ('EAN', 'Nazwa', 'Ilość', 'Lokalizacja', 'Data ważności', 'Data wprowadzenia')

        configure_treeview(columns, headings)

        query = '''
                SELECT p.EAN, p.name, i.quantity, i.location, i.expiration_date, i.entry_date
                FROM products p
                LEFT JOIN inventory i ON p.product_id = i.product_id
                LEFT JOIN transactions t ON p.product_id = t.product_id
                WHERE p.EAN = %s
        '''
        def find_by_ean_click():
            try:
                with get_conn() as my_conn:
                    with my_conn.cursor() as cursor:
                        cursor.execute("USE wms")
                        ean_to_compare = ean.get()
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
                cursor.close()
        root.bind('<Return>',lambda event:find_by_ean_click())

    def overall_sent():
        columns = ('EAN', 'Name', 'Qty Sell', 'Date')
        headings = ('EAN', 'Nazwa', 'Wysłane', 'Data')

        configure_treeview(columns, headings)

        date = waznosc.get()

        if date == '':
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
                cursor.close()
                
    def actual_stock():
        columns = ('EAN', "name", 'qty_difference', 'expiration_date', 'location')
        headings = ('EAN', "Nazwa", 'Stan', 'Data waznosci','Lokalizacja')

        configure_treeview(columns, headings)
        
        query = '''
        SELECT
            p.EAN, 
            p.name,
            COALESCE(i.total_quantity, 0) - COALESCE(SUM(t.qty), 0) AS qty_difference,
            MAX(COALESCE(i.expiration_date, 'No expiration date')) AS expiration_date,
            MAX(COALESCE(i.location, 'No location')) AS location,
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
                SELECT product_id, SUM(quantity) AS total_quantity, MAX(expiration_date) AS expiration_date, MAX(location) AS location
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

    def display_expirations():
        columns = ('EAN', 'Name', 'Qty', 'Location', 'Expiration Date')
        headings = ('EAN', 'Nazwa', 'Ilość', 'Lokalizacja', 'Data ważności')

        configure_treeview(columns, headings)

        query = '''
                SELECT subquery.EAN, subquery.name, subquery.qty_difference, subquery.location, subquery.expiration_date
                FROM (
                    SELECT p.EAN, p.name, 
                        SUM(COALESCE(i.quantity, 0) - COALESCE(t.qty, 0)) AS qty_difference,
                        MAX(i.expiration_date) AS expiration_date,
                        MAX(i.location) AS location
                    FROM products p
                        JOIN inventory i ON p.product_id = i.product_id
                        LEFT JOIN transactions t ON p.product_id = t.product_id
                        WHERE (i.expiration_date BETWEEN CURDATE() AND CURDATE() + INTERVAL 7 DAY)
                            OR (i.expiration_date < CURDATE())
                    GROUP BY p.EAN, p.name
                ) AS subquery;
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

    def base_stock():
        date = waznosc.get()
        columns = ('EAN', 'Name', 'Location', 'Remaining qty', 'Qty Entry', 'Qty Sell', 'Entry Date')
        headings = ('EAN', 'Nazwa', 'Lokalizacja', 'Remaining Qty', 'Ilość wprowadzonych', 'Wysłane', ' Data wprowadzenia')

        configure_treeview(columns, headings)
        date = waznosc.get()

        query = '''
                    SELECT
                        q1.EAN,
                        q1.name,
                        q1.location,
                        q2.total_quantity,
                        q1.qty_difference,
                        q2.total_quantity - q1.qty_difference AS remaining_quantity,
                        q2.entry_date
                    FROM (
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
                    ) q1
                    JOIN (
                        SELECT
                            p.EAN,
                            p.name,
                            i.entry_date,
                            SUM(COALESCE(i.quantity, 0)) AS total_quantity
                        FROM
                            products p
                        LEFT JOIN
                            inventory i ON p.product_id = i.product_id
                        LEFT JOIN
                            transactions t ON p.product_id = t.product_id
                        WHERE
                            i.entry_date = %s
                        GROUP BY
                            p.EAN, p.name, i.entry_date
                        ORDER BY
                            p.EAN, i.entry_date
                    ) q2 ON q1.EAN = q2.EAN AND q1.name = q2.name;
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
            operations.update()

        except mysql.connector.Error as err:
            print(f"Error executing query: {err}")
        finally:
            cursor.close()

    def show_eveything():
        columns = ('ID','EAN', 'Name', 'Location', 'Entry qty', 'Qty Sell', 'Remaining Quantity', 'Entry Date')
        headings = ('ID','EAN', 'Nazwa', 'Lokalizacja', 'Ilość wprowadzonych', 'Wysłane','Remaining Quantity', 'Data wprowadzenia')

        configure_treeview(columns, headings)

        query = """
SELECT
    q1.product_id,
    q1.EAN,
    q1.name,
    q1.location,
    q2.total_quantity,
    q1.qty_difference,
    q2.total_quantity - q1.qty_difference AS remaining_quantity,
    q2.entry_date
FROM (
    SELECT
        p.product_id,
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
    WHERE
        i.entry_date BETWEEN '2023-01-01' AND '2023-01-07'  -- Specify your date range here
    GROUP BY
        p.product_id, p.EAN, p.name
) q1
JOIN (
    SELECT
        p.product_id,
        p.EAN,
        p.name,
        i.entry_date,
        SUM(COALESCE(i.quantity, 0)) AS total_quantity
    FROM
        products p
    LEFT JOIN
        inventory i ON p.product_id = i.product_id
    LEFT JOIN
        transactions t ON p.product_id = t.product_id
    WHERE
        i.entry_date BETWEEN '2023-01-01' AND '2023-12-31'  -- Specify your date range here
    GROUP BY
        p.product_id, p.EAN, p.name, i.entry_date
    ORDER BY
        p.EAN, i.entry_date
) q2 ON q1.product_id = q2.product_id AND q1.EAN = q2.EAN AND q1.name = q2.name;
"""

        # query = '''
        #             SELECT
        #                 q1.product_id,
        #                 q1.EAN,
        #                 q1.name,
        #                 q1.location,
        #                 q2.total_quantity,
        #                 q1.qty_difference,
        #                 q2.total_quantity - q1.qty_difference AS remaining_quantity,
        #                 q2.entry_date
        #             FROM (
        #                 SELECT
        #                     p.product_id,
        #                     p.EAN,
        #                     p.name,
        #                     MAX(i.quantity) AS quantity,
        #                     MAX(i.location) AS location,
        #                     MAX(i.expiration_date) AS expiration_date,
        #                     SUM(COALESCE(i.quantity, 0) - COALESCE(t.qty, 0)) AS qty_difference,
        #                     MAX(i.entry_date) AS entry_date
        #                 FROM
        #                     products p
        #                 LEFT JOIN
        #                     inventory i ON p.product_id = i.product_id
        #                 LEFT JOIN
        #                     transactions t ON p.product_id = t.product_id
        #                 GROUP BY
        #                     p.product_id, p.EAN, p.name
        #             ) q1
        #             JOIN (
        #                 SELECT
        #                     p.product_id,
        #                     p.EAN,
        #                     p.name,
        #                     i.entry_date,
        #                     SUM(COALESCE(i.quantity, 0)) AS total_quantity
        #                 FROM
        #                     products p
        #                 LEFT JOIN
        #                     inventory i ON p.product_id = i.product_id
        #                 LEFT JOIN
        #                     transactions t ON p.product_id = t.product_id
        #                 GROUP BY
        #                     p.product_id, p.EAN, p.name, i.entry_date
        #                 ORDER BY
        #                     p.EAN, i.entry_date
        #             ) q2 ON q1.product_id = q2.product_id AND q1.EAN = q2.EAN AND q1.name = q2.name;
        # '''
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

    upper_gui.pack(side=tk.TOP)
    upper_gui.pack_propagate(False)
    operations.pack()
    operations.pack(expand=tk.YES, fill=tk.BOTH)

    def ref():
        for item in operations.get_children():
            operations.delete(item)

        operations.update()
    realtime_stock_mode()
    root.mainloop()
main()