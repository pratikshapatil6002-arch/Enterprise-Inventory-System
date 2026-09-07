from database import get_connection


# Get all products
def get_all_products():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM products")
    products = cursor.fetchall()

    conn.close()

    return products

#Add product
def add_product(product_name, price, quantity):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO products (product_name, price, quantity)
        VALUES (?, ?, ?)
    """, (product_name, price, quantity))

    conn.commit()
    conn.close()
    
# Delete product
def delete_product_db(id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM products WHERE id = ?", (id,))

    conn.commit()
    conn.close()


# Get single product
def get_product(id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM products WHERE id = ?",
        (id,)
    )

    product = cursor.fetchone()

    conn.close()

    return product

#update product

def update_product_db(id, product_name, price, quantity):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE products
        SET product_name = ?, price = ?, quantity = ?
        WHERE id = ?
    """, (product_name, price, quantity, id))

    conn.commit()
    conn.close()

# Search Products
def search_products(search):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM products
        WHERE product_name LIKE ?
    """, ('%' + search + '%',))

    products = cursor.fetchall()
    conn.close()

    return products

# Get Low Stock Products
def get_low_stock_products():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM products WHERE quantity < 5"
    )

    low_stock_products = cursor.fetchall()

    conn.close()

    return low_stock_products


# Add Activity
def add_activity(activity):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO activity_log (activity) VALUES (?)",
        (activity,)
    )

    conn.commit()
    conn.close()


# Get Recent Activities
def get_recent_activities():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT activity, created_at
        FROM activity_log
        ORDER BY id DESC
        LIMIT 5
    """)

    activities = cursor.fetchall()

    conn.close()

    return activities