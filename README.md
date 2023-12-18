# Warehouse Management System (WMS)

## Overview

This Warehouse Management System (WMS) is a Python-based application designed to manage and optimize warehouse operations. It utilizes MySQL as the database backend for efficient data storage and retrieval.

## Features

- **Inventory Management:** Keep track of products, quantities, and locations within the warehouse.
- **Transaction Tracking:** Record and manage stock movements through various transactions.
- **Expiration Date Management:** Monitor product expiration dates for better inventory control.
- **User-Friendly Interface:** Accessible through a user-friendly command-line interface.

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [Configuration](#configuration)
- [Database Schema](#database-schema)
- [Contributing](#contributing)
- [License](#license)

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/psmajkos/WMS.git

## Usage

1. **Run the Application:**
   - Double-click the executable file or run the following command to start the WMS application:

     ```bash
     python main.py
     ```

2. **Explore the Graphical User Interface:**
   - Navigate through the user-friendly GUI to perform various operations. Interact with the provided buttons, input fields, and menus.

3. **Demonstrate Basic Operations:**
   - Perform basic operations using the GUI. For example, adding a new product might involve the following steps:
     - Click on the "Add Product" button.
     - Enter the product details in the provided fields.
     - Click "Submit" to add the product.

4. **Additional Configuration:**
   - If there are any additional configurations or settings, provide clear instructions on how users can configure the application within the GUI.

5. **Troubleshooting:**
   - Include information on how users can troubleshoot common issues or errors related to the GUI-based application.

## Configuration

1. Change the connection data (db_connector.py) 
def get_conn():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        passwd=""
    )

    host - your connection name
    user - username
    passwd - password

## Database Schema

# Table: products

| Column Name   | Data Type        | Description                        |
|---------------|------------------|------------------------------------|
| product_id    | INT              | Primary key for the products table |
| EAN           | BIGINT NOT NULL  | Product identifier                 |
| name          | VARCHAR(80)      | Name of the product                 |
| category      | VARCHAR(80)      | Category of the product             |

# Table: inventory

| Column Name      | Data Type         | Description                               |
|------------------|-------------------|-------------------------------------------|
| inventory_id     | INT               | Primary key for the inventory table       |
| product_id       | INT               | Foreign key referencing products table   |
| quantity         | INT               | Quantity of the product in inventory      |
| location         | VARCHAR(255)      | Location of the product in inventory      |
| expiration_date  | DATE              | Expiration date of the product (nullable) |
| entry_date       | DATE              | Date of entry into inventory              |

# Table: transactions

| Column Name       | Data Type         | Description                               |
|-------------------|-------------------|-------------------------------------------|
| id                | INT               | Primary key for the transactions table    |
| product_id        | INT               | Foreign key referencing products table   |
| qty               | INT               | Quantity of the product in the transaction|
| transaction_date  | DATE              | Date of the transaction                   |
