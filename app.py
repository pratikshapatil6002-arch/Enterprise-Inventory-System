from flask import Flask, render_template, request, redirect, url_for, session, flash
from database import create_database, get_connection
from config import SECRET_KEY
from models import *
from dashboard import get_dashboard_data
from auth import check_login

app = Flask(__name__)
app.secret_key = SECRET_KEY

# Home Page (Login Page)
@app.route('/')
def home():
    return render_template("login.html")
@app.route('/register')
def register_page():
    return render_template("register.html")

@app.route('/register', methods=['POST'])
def register():

    name = request.form['name']
    email = request.form['email']
    password = request.form['password']

    conn = get_connection()
    cursor = conn.cursor()

    # Check if email already exists
    cursor.execute("SELECT * FROM users WHERE email=?", (email,))
    existing = cursor.fetchone()

    if existing:
        conn.close()
        flash("Email already registered!")
        return redirect(url_for('home'))

    # Insert new user
    cursor.execute(
        "INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
        (name, email, password)
    )
    conn.commit()
    conn.close()

    # Automatically log in the new user
    session['user'] = name
    session['role'] = "user"

    return redirect(url_for('user_dashboard'))
# Login Route
@app.route('/login', methods=['POST'])
def login():

    username = request.form['username']
    password = request.form['password']

    result = check_login(username, password)

    if result:
        role, name = result

        session['user'] = name
        session['role'] = role

        # Admin Login
        if role == "admin":
            return redirect(url_for('dashboard'))

        # User Login
        else:
            return redirect(url_for('user_dashboard'))

    flash("Invalid Username or Password")
    return redirect(url_for('home'))


# ===========================
# USER DASHBOARD ROUTE
# ===========================
@app.route('/user_dashboard')
def user_dashboard():

    if 'user' not in session or session.get('role') != "user":
        return redirect(url_for('home'))

    products = get_all_products()

    return render_template(
        'user_home.html',
        user_name=session['user'],
        products=products
    )

# Logout Route
@app.route('/logout')
def logout():

    session.pop('user', None)
    session.pop('role', None)

    return redirect(url_for('home'))

# dashboard route
@app.route('/dashboard')
def dashboard():

    if 'user' not in session:
        return redirect(url_for('home'))

    # Only Admin can open Dashboard
    if session.get('role') != "admin":
        return redirect(url_for('user_home'))

    (
        total_products,
        total_quantity,
        total_value,
        low_stock,
        low_stock_products,
        recent_products,
        recent_activities
    ) = get_dashboard_data()

    return render_template(
        'dashboard.html',
        total_products=total_products,
        total_quantity=total_quantity,
        total_value=total_value,
        low_stock=low_stock,
        low_stock_products=low_stock_products,
        recent_products=recent_products,
        recent_activities=recent_activities
    )
# User Home Route
@app.route('/user_home')
def user_home():

    if 'user' not in session:
        return redirect(url_for('home'))

    if session.get('role') != "user":
        return redirect(url_for('dashboard'))

    products = get_all_products()

    return render_template(
        'user_home.html',
        products=products,
        user_name=session['user']
    )
# Analytics Route

@app.route('/analytics')
def analytics():

    if 'user' not in session:
        return redirect(url_for('home'))

    products = get_all_products()

    analytics_products = []

    maximum_quantity = 0

    # Find highest quantity
    for product in products:

        quantity = product[3]

        if quantity > maximum_quantity:
            maximum_quantity = quantity


    # Prepare analytics data
    for product in products:

        product_id = product[0]
        product_name = product[1]
        price = product[2]
        quantity = product[3]

        # Stock percentage
        if maximum_quantity > 0:
            percentage = (quantity / maximum_quantity) * 100
        else:
            percentage = 0

        # Inventory value
        inventory_value = price * quantity

        # Stock status
        if quantity == 0:
            stock_status = "Out of Stock"

        elif quantity < 5:
            stock_status = "Low Stock"

        else:
            stock_status = "Healthy"

        analytics_products.append(
            (
                product_id,
                product_name,
                price,
                quantity,
                percentage,
                inventory_value,
                stock_status
            )
        )


    # Total inventory value
    total_inventory_value = 0

    for product in products:

        total_inventory_value += product[2] * product[3]


    # Highest quantity product
    highest_stock_product = None

    if products:

        highest_stock_product = max(
            products,
            key=lambda product: product[3]
        )


    # Highest value product
    highest_value_product = None

    if products:

        highest_value_product = max(
            products,
            key=lambda product: product[2] * product[3]
        )


    # Low stock products
    low_stock_products = []

    for product in products:

        if product[3] < 5:
            low_stock_products.append(product)


    return render_template(
        'analytics.html',
        products=analytics_products,
        total_inventory_value=total_inventory_value,
        highest_stock_product=highest_stock_product,
        highest_value_product=highest_value_product,
        low_stock_products=low_stock_products
    )

# Delete Product Route
@app.route('/delete_product/<int:id>')
def delete_product(id):

    if 'user' not in session:
        return redirect(url_for('home'))

    delete_product_db(id)

    flash("🗑️ Product deleted successfully!")
    return redirect(url_for('products'))

# Products Route
@app.route('/products')
def products():

    if 'user' not in session:
        return redirect(url_for('home'))

    products = get_all_products()

    return render_template('products.html', products=products)

# Search Product Route
@app.route('/search_product')
def search_product():

    if 'user' not in session:
        return redirect(url_for('home'))

    search = request.args['search']

    print("Searching for:", search)

    products = search_products(search)

    print("Result:", products)

    return render_template('products.html', products=products)

@app.route('/change_password', methods=['POST'])
def change_password():

    if 'user' not in session:
        return redirect('/')

    from config import PASSWORD

    old_password = request.form['old_password']
    new_password = request.form['new_password']


    if old_password == PASSWORD:

        import config
        config.PASSWORD = new_password

        return "Password Changed Successfully"

    else:

        return "Old Password Incorrect"


# Add Product Route
@app.route('/add_product')
def add_product_page():

    if 'user' not in session:
        return redirect(url_for('home'))

    return render_template('add_product.html')

@app.route('/save_product', methods=['POST'])
def save_product():

    if 'user' not in session:
        return redirect(url_for('home'))

    product_name = request.form['product_name']
    price = float(request.form['price'])
    quantity = int(request.form['quantity'])

    # Validation
    if price < 0:
        flash("❌ Price cannot be negative!")
        return redirect(url_for('add_product'))

    if quantity < 0:
        flash("❌ Quantity cannot be negative!")
        return redirect(url_for('add_product'))

    add_product(product_name, price, quantity)

    add_activity(f"Product Added: {product_name}")
    flash("✅ Product added successfully!")

    return redirect(url_for('products'))

# Edit Product Route
@app.route('/edit_product/<int:id>')
def edit_product(id):

    if 'user' not in session:
        return redirect(url_for('home'))

    product = get_product(id)

    return render_template('edit_product.html', product=product)

# Update Product Route
@app.route('/update_product', methods=['POST'])
def update_product():

    if 'user' not in session:
        return redirect(url_for('home'))

    id = request.form['id']
    product_name = request.form['product_name']
    price = request.form['price']
    quantity = request.form['quantity']

    update_product_db(id, product_name, price, quantity)

    add_activity(f"Product Updated: {product_name}")
    flash("✏️ Product updated successfully!")

    return redirect(url_for('products'))

# Run the Application
# Run the Application
if __name__ == '__main__':
    create_database()
    app.run(host='0.0.0.0', port=5000, debug=True)