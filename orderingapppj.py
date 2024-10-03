import streamlit as st
import pandas as pd
import sqlite3
import schedule
import time
from datetime import datetime

# Database connection
conn = sqlite3.connect('material_orders.db', check_same_thread=False)
c = conn.cursor()

# Create table if not exists
c.execute('''CREATE TABLE IF NOT EXISTS orders
             (id INTEGER PRIMARY KEY AUTOINCREMENT, job_name TEXT, material_name TEXT, quantity INTEGER, status TEXT,
              supplier TEXT, order_date TEXT, expected_delivery_date TEXT, ordered_by TEXT, order_reference TEXT,
              comments TEXT, reminder_frequency TEXT, recipient_emails TEXT)''')
conn.commit()

# Add a new order
def add_order(job_name, material_names, quantities, status, supplier, order_date, expected_delivery_date, ordered_by, order_reference, comments, reminder_frequency, recipient_emails):
    for material_name, quantity in zip(material_names, quantities):
        c.execute('''INSERT INTO orders (job_name, material_name, quantity, status, supplier, order_date, expected_delivery_date, ordered_by, order_reference, comments, reminder_frequency, recipient_emails)
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                  (job_name, material_name, quantity, status, supplier, order_date, expected_delivery_date, ordered_by, order_reference, comments, reminder_frequency, recipient_emails))
    conn.commit()

# Get all orders
def get_orders():
    c.execute('SELECT * FROM orders')
    return c.fetchall()

# Update the status of an order
def update_order_status(order_id, new_status):
    c.execute('UPDATE orders SET status = ? WHERE id = ?', (new_status, order_id))
    conn.commit()

# Delete an order
def delete_order(order_id):
    c.execute('DELETE FROM orders WHERE id = ?', (order_id,))
    conn.commit()

# Streamlit App
st.title("Electrical Material Order Tracking App")

# Add a new order
st.header("Add a New Order")
job_name = st.text_input("Job Name")
material_count = st.number_input("How many materials would you like to add?", min_value=1, step=1)
material_names = []
quantities = []

for i in range(material_count):
    material_name = st.text_input(f"Material Name #{i + 1}")
    quantity = st.number_input(f"Quantity for Material #{i + 1}", min_value=1, step=1)
    material_names.append(material_name)
    quantities.append(quantity)

status = st.selectbox("Status", ["To be Ordered", "Ordered", "Delivered"])
supplier = st.text_input("Supplier")
order_date = st.date_input("Order Date")
expected_delivery_date = st.date_input("Expected Delivery Date")
ordered_by = st.text_input("Ordered By")
order_reference = st.text_input("Order Reference/PO Number")
comments = st.text_area("Comments")
reminder_frequency = st.selectbox("How often would you like a reminder?", ["None", "Daily", "Weekly", "Bi-Weekly", "Monthly"])
recipient_emails = st.multiselect("Select Recipient Emails", ["landis@pjselectric.ca", "miguel@pjselectric.ca", "jason@pjselectric.ca"])

if st.button("Add Order"):
    add_order(job_name, material_names, quantities, status, supplier, order_date.strftime("%Y-%m-%d"),
              expected_delivery_date.strftime("%Y-%m-%d"), ordered_by, order_reference, comments, reminder_frequency,
              ", ".join(recipient_emails))
    st.success("Order added successfully!")

# View and update orders
st.header("View and Update Orders")
orders = get_orders()
if orders:
    df = pd.DataFrame(orders, columns=['ID', 'Job Name', 'Material Name', 'Quantity', 'Status', 'Supplier', 'Order Date',
                                       'Expected Delivery Date', 'Ordered By', 'Order Reference', 'Comments',
                                       'Reminder Frequency', 'Recipient Emails'])
    st.dataframe(df)

    order_id_to_update = st.number_input("Enter the Order ID to Update Status", min_value=1, step=1)
    new_status = st.selectbox("New Status", ["To be Ordered", "Ordered", "Delivered"])

    if st.button("Update Status"):
        update_order_status(order_id_to_update, new_status)
        st.success(f"Order ID {order_id_to_update} updated to {new_status}")

# Delete an order
st.header("Delete an Order")
order_id_to_delete = st.number_input("Enter the Order ID to Delete", min_value=1, step=1)
if st.button("Delete Order"):
    delete_order(order_id_to_delete)
    st.success(f"Order ID {order_id_to_delete} deleted successfully")

# Reminder scheduling (run in the background)
def send_reminder():
    orders = get_orders()
    for order in orders:
        order_id, job_name, material_name, quantity, status, supplier, order_date, expected_delivery_date, ordered_by, order_reference, comments, reminder_frequency, recipient_emails = order
        if status == "To be Ordered" and reminder_frequency != "None":
            st.write(f"Reminder: Order {material_name} for Job {job_name} needs to be placed.")
            # You can add actual email sending code here

# Scheduler setup
def run_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(1)

# Schedule reminders
schedule.every().day.at("09:00").do(send_reminder)

# Note: For real-world applications, consider running reminders separately