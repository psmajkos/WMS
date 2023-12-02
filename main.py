import mysql.connector
import tkinter as tk
from tkinter import ttk, Frame, NO, IntVar, Radiobutton, SUNKEN, HORIZONTAL, messagebox,Text, Checkbutton
from tkcalendar import DateEntry
from datetime import datetime
import babel.numbers

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

    root = tk.Tk()
    root.title("Product Inventory")

    # Set geometry to cover the whole screen
    root.geometry("{0}x{1}+0+0".format(root.winfo_screenwidth(), root.winfo_screenheight()))

    # Allow the window to be resizable
    root.resizable(True, True)


    EAN = tk.IntVar()
    qty = tk.IntVar()
    name = tk.StringVar()
    waznosc = tk.StringVar()
    location_var = tk.StringVar()
    include_expiration_var = IntVar()
    include_expiration_var.set(1)  # Set default to include expiration

    EAN.set("")
    qty.set(1)

    def add_product():
        get_ean = EAN.get()
        name_get = name.get()

        # Check if the EAN and name are not empty
        if not get_ean:
            messagebox.showerror("Błąd", "EAN i nazwa są wymagane!")
            return
        
        # Check if the EAN already exists
        ean_exists_query = "SELECT COUNT(*) FROM products WHERE EAN = %s"
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

        # Clear the entry field after inserting the value
        EAN_entry.delete(0, tk.END)
        qty.set(1)
        name_entry.delete(0, tk.END)
        ref()
        # realtime_stock()
        # actual_stock()

    def put_product_to_inventory(include_expiration=True):
        get_ean = EAN.get()
        get_qty = qty.get()
        location = location_var.get()

        if get_qty is None:
            get_qty = 1

        # Check if the EAN and name are not empty
        if not get_ean or not get_qty:
            messagebox.showerror("Błąd!", "EAN i Ilość są wymagane!")
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
                        if include_expiration:
                            query = "INSERT INTO inventory(product_id, quantity, location, expiration_date, entry_date) VALUES (%s, %s, %s, %s, %s)"
                            values = (product_id[0], get_qty, location, waznosc.get(), formatted_date)
                        else:
                            query = "INSERT INTO inventory(product_id, quantity, location, entry_date) VALUES (%s, %s, %s, %s)"
                            values = (product_id[0], get_qty, location, formatted_date)

                        cursor.execute(query, values)
                        my_conn.commit()
                    else:
                        print("Produktu nie znaleziono.")

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
        actual_stock()


    def packing():
        get_ean = EAN.get()
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
            # Close the cursor (optional, as you will close it when the application exits)
            cursor.close()

        # Clear the entry field after inserting the value
        EAN_entry.delete(0, tk.END)
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

    upper_gui = tk.Frame(root, width=1920, height=500, bd=2, relief=SUNKEN)

    # Create the Checkbutton
    expiration_checkbutton = Checkbutton(upper_gui, text="Z datą ważności", variable=include_expiration_var)

    # Attach the function to the checkbutton state change
    expiration_checkbutton.config(command=handle_expiration_check)

    EAN_label = tk.Label(upper_gui, text="EAN: ")
    EAN_entry = ttk.Entry(upper_gui, textvariable=EAN)
    qty_entry = ttk.Entry(upper_gui, textvariable=qty, width=3)
    qty_label = tk.Label(upper_gui, text="Ilość: ", width=7)
    name_label = tk.Label(upper_gui, text="Nazwa: ", width=10)
    name_entry = ttk.Entry(upper_gui, textvariable=name)
    waznosc_label = tk.Label(upper_gui, text="Ważność", width=10)
    waznosc_entry = DateEntry(upper_gui, textvariable=waznosc, date_pattern='y/m/d')
    
    send_button = ttk.Button(upper_gui, text="Nadaj", command=packing)
    location_label = ttk.Label(upper_gui, text="Lokalizacja")
    location_combo = ttk.Combobox(upper_gui, text="Lokalizacja", textvariable=location_var)
    location_combo['values'] = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H',]
    add_button = ttk.Button(upper_gui, text="Dodaj do bazy", command=add_product)

    # Add a button for putting data into inventory
    put_into_inventory_button = ttk.Button(upper_gui, text="Dodaj partie", command=put_product_to_inventory)
    put_into_inventory_button.pack()

    root.bind('<Return>',lambda event:put_product_to_inventory())

    root.bind('<Return>',lambda event:add_product())

    EAN_label.pack()
    EAN_entry.pack()
    name_label.pack()
    name_entry.pack()
    EAN_entry.focus_set()
    qty_label.pack()
    qty_entry.pack()

    waznosc_label.pack()
    waznosc_entry.pack()

    send_button.pack()
    location_label.pack()
    location_combo.pack()
    add_button.pack()
    expiration_checkbutton.pack()

    def show_widgets(widgets):
        for widget in widgets:
            widget.pack()

    def hide_widgets(widgets):
        for widget in widgets:
            widget.pack_forget()

    def sent_today_widgets():
        show_widgets([send_button, copy_button, EAN_label, EAN_entry])
        hide_widgets([add_button, waznosc_label, waznosc_entry, qty_label, qty_entry, location_label, location_combo, put_into_inventory_button, name_entry, name_label, expiration_checkbutton])

    def actual_mode_widgets():
        show_widgets([qty_label, qty_entry, waznosc_label, waznosc_entry, location_label, location_combo, copy_button, put_into_inventory_button, expiration_checkbutton])
        hide_widgets([send_button, name_entry, name_label, add_button])

    def add_product_mode_widgets():
        show_widgets([EAN_label, EAN_entry, name_label, name_entry, add_button])
        hide_widgets([waznosc_entry, waznosc_label, qty_entry, qty_label, location_combo, location_label, copy_button, send_button, put_into_inventory_button, expiration_checkbutton])

    def overall_mode_widgets():
        show_widgets([send_button, waznosc_label, waznosc_entry])
        hide_widgets([add_button, waznosc_entry, waznosc_label, qty_entry, qty_label, location_combo, location_label, copy_button, put_into_inventory_button, expiration_checkbutton])

    def find_by_ean_mode_widgets():
        show_widgets([copy_button, EAN_label, EAN_entry])
        hide_widgets([name_entry, name_label, waznosc_entry, waznosc_label, qty_entry, qty_label, location_combo, location_label, send_button, put_into_inventory_button, add_button, expiration_checkbutton])

    def total_stock_mode_widgets():
        show_widgets([copy_button, waznosc_label,waznosc_entry])
        hide_widgets([EAN_entry, EAN_label, name_entry, name_label ,add_button, qty_entry, qty_label, location_combo, location_label, copy_button, send_button, put_into_inventory_button,expiration_checkbutton])

    def show_eveything_widgets():
        hide_widgets([copy_button, waznosc_label,waznosc_entry])
        show_widgets([copy_button, waznosc_label, waznosc_entry, EAN_entry, EAN_label, name_entry, name_label ,add_button, qty_entry, qty_label, location_combo, location_label, copy_button, send_button, put_into_inventory_button,expiration_checkbutton])
    
    def sent_today_mode():
        sent_today_widgets()
        today_table()

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

    radio_frame = tk.Frame(root, bd=2, relief=SUNKEN)

    def copy_ean():
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
                                    SET quantity = %s, location = %s 
                                    WHERE product_id = %s;"""
                            values = (qty.get(), waznosc.get(), product_id[0])

                            cursor.execute(query, values)
                            my_conn.commit()
                            print("Row updated successfully.")
                        else:
                            print("Product not found.")

            except mysql.connector.Error as err:
                print(f"Error executing query: {err}")
            finally:
                # Close the cursor (optional, as you will close it when the application exits)
                cursor.close()
        else:
            print("Not enough values in the tuple.")




    mode_of_transportation = ttk.Label(radio_frame, text="Model pracy: ")
    mode_of_transportation.pack()

# horizontal separator
    ttk.Separator(
        master=radio_frame,
        orient=HORIZONTAL,
        style='blue.TSeparator',
        class_= ttk.Separator,
        takefocus= 1,
        cursor='plus'    
    ).pack()
        
    r = IntVar()
    # Modify your radio buttons' commands to call the corresponding mode functions
    add_product_radio = Radiobutton(radio_frame, text="Dodaj EAN do bazy",
                        variable=r, value=1, highlightthickness=0, command=add_product_mode)
    actual_radio = Radiobutton(radio_frame, text="Aktualny stan",
                        variable=r, value=0, highlightthickness=0, command=realtime_stock_mode)
    find_by_ean_radio = Radiobutton(radio_frame, text="Znajdz po EAN",
                        variable=r, value=4, highlightthickness=0, command=find_by_ean_mode)
    normal = Radiobutton(radio_frame, text="Wysyłka",
                        variable=r, value=2, highlightthickness=0, command=sent_today_mode)
    overall_radio = Radiobutton(radio_frame, text="Wszystkie wysłane",
                        variable=r, value=3, highlightthickness=0, command=overall_mode)
    # total_stock_radio = Radiobutton(radio_frame, text="Wszystko",
    #                     variable=r, value=5, highlightthickness=0, command=total_stock_mode)
    
    expiration_stock_radio = Radiobutton(radio_frame, text="Krótka data",
                    variable=r, value=6, highlightthickness=0, command=expiration_mode)
    
    everything = Radiobutton(radio_frame, text="Wszystko",
                    variable=r, value=7, highlightthickness=0, command=show_eveything_mode)
    
    add_product_radio.pack()
    actual_radio.pack()
    find_by_ean_radio.pack()
    normal.pack()
    overall_radio.pack()
    # total_stock_radio.pack()
    expiration_stock_radio.pack()
    everything.pack()

    # Create a button for copying EAN
    copy_button = ttk.Button(radio_frame, text="Kopiuj EAN", command=copy_ean)
    copy_button.pack() # Adjust the row and column as needed

    # # Create a button for copying EAN
    edit_button = ttk.Button(radio_frame, text="Edit row", command=edit_row)
    edit_button.pack() # Adjust the row and column as needed

    radio_frame.pack(side=tk.RIGHT)

    operations_frame = Frame(root, bd=2, width=1920, height=400, relief=SUNKEN)
    operations_frame.pack(side='bottom')
    operations_frame.pack_propagate(False)

    operations = ttk.Treeview(operations_frame, height=20)

    operations.column("#0", width=0,  stretch=NO)

    def today_table():
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
            # Close the cursor
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
                        ean_to_compare = EAN.get()
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
                
    def actual_stock():
        columns = ('EAN', "name", 'qty_difference', 'quantity_comparison')
        headings = ('EAN', "Nazwa", 'Stan','quantity_comparison')

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
                    WHERE i.expiration_date BETWEEN CURDATE() AND CURDATE() + INTERVAL 7 DAY
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

        query = '''
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
                        GROUP BY
                            p.product_id, p.EAN, p.name, i.entry_date
                        ORDER BY
                            p.EAN, i.entry_date
                    ) q2 ON q1.product_id = q2.product_id AND q1.EAN = q2.EAN AND q1.name = q2.name;
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

    upper_gui.pack(side=tk.TOP)
    upper_gui.pack_propagate(False)
    operations.pack()
    operations.pack(expand=tk.YES, fill=tk.BOTH)

    def ref():
        for item in operations.get_children():
            operations.delete(item)

        operations.update()
        operations.pack() 
    # actual_stock()
    realtime_stock_mode()
    root.mainloop()
main()