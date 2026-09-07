from database import get_connection
from models import get_recent_activities


def get_dashboard_data():

    conn = get_connection()
    cursor = conn.cursor()


    # Total Products
    cursor.execute("SELECT COUNT(*) FROM products")
    total_products = cursor.fetchone()[0]


    # Total Quantity
    cursor.execute("SELECT SUM(quantity) FROM products")
    total_quantity = cursor.fetchone()[0] or 0


    # Total Inventory Value
    cursor.execute("SELECT SUM(price * quantity) FROM products")
    total_value = cursor.fetchone()[0] or 0


    # Low Stock Count
    cursor.execute(
        "SELECT COUNT(*) FROM products WHERE quantity < 5"
    )
    low_stock = cursor.fetchone()[0]


    # Low Stock Product Details
    cursor.execute(
        "SELECT * FROM products WHERE quantity < 5"
    )
    low_stock_products = cursor.fetchall()



    # Recent Products
    cursor.execute(
        "SELECT * FROM products ORDER BY id DESC LIMIT 5"
    )
    recent_products = cursor.fetchall()

    # Recent Activities
    recent_activities = get_recent_activities()


    conn.close()
    return (
        total_products,
        total_quantity,
        total_value,
        low_stock,
        low_stock_products,
        recent_products,
        recent_activities
    )