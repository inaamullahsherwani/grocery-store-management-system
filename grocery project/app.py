from flask import Flask, render_template, request, redirect
import mysql.connector

app = Flask(__name__)

db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Inaam@1234#',
    'database': 'grocery'
}

def connect_db():
    return mysql.connector.connect(**db_config)

# --- Define Routes ---
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/products')
def products():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Product;")
    products = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('index.html', products=products)

@app.route('/low-stock')
def low_stock():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Product WHERE stock_quantity < 100;")
    low_stock_products = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('index.html', low_stock_products=low_stock_products)

@app.route('/near-expiry')
def near_expiry():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Product WHERE expiry_date <= CURDATE() + INTERVAL 7 DAY;")
    near_expiry_products = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('index.html', near_expiry_products=near_expiry_products)

# supply summary--------------------------------------------------------------------------------------------------

@app.route('/supply-summary')
def supply_summary():
    conn = connect_db()
    cursor = conn.cursor()
    query = """
        SELECT s.supplier_id, s.name, s.contact_info, SUM(sp.quantity_supplied) AS total_quantity
        FROM Supplier s
        JOIN Supply sp ON s.supplier_id = sp.supplier_id
        GROUP BY s.supplier_id, s.name, s.contact_info;
    """
    cursor.execute(query)
    supply_data = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('index.html', supply_data=supply_data)



# total stock by category--------------------------------------------------------------------------------------

@app.route('/stock-summary')
def stock_summary():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT category, COUNT(*) AS product_count, SUM(stock_quantity) AS total_stock
        FROM Product
        GROUP BY category;
    """)
    summary = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('index.html', stock_summary=summary)

# expired products

@app.route('/expired-products')
def expired_products():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Product WHERE expiry_date <= CURDATE();")
    expired_products = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('index.html', expired_products=expired_products)

# --- Add Product Page ---
@app.route('/add-product', methods=['GET', 'POST'])
def add_product():
    if request.method == 'POST':
        name = request.form['name']
        category = request.form['category']
        price = float(request.form['price'])
        stock = int(request.form['stock'])
        expiry = request.form['expiry']

        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO Product (name, category, price, stock_quantity, expiry_date)
            VALUES (%s, %s, %s, %s, %s)
        """, (name, category, price, stock, expiry))
        conn.commit()
        cursor.close()
        conn.close()

        return redirect('/products')  # Show all products after adding

    return render_template('add_product.html')



# out of stock------------------------------------------------------------------------------------------------------------------


@app.route('/out-of-stock')
def out_of_stock():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Product WHERE stock_quantity = 0;")
    out_of_stock = cursor.fetchall()
    print("DEBUG - OUT OF STOCK:", out_of_stock)  # Add this temporarily
    cursor.close()
    conn.close()
    return render_template('index.html', out_of_stock=out_of_stock)


# --- Update Product ---
@app.route('/update-product/<int:product_id>', methods=['GET', 'POST'])
def update_product(product_id):
    conn = connect_db()
    cursor = conn.cursor()

    if request.method == 'POST':
        name = request.form['name']
        category = request.form['category']
        price = float(request.form['price'])
        stock = int(request.form['stock'])
        expiry = request.form['expiry']

        cursor.execute("""
            UPDATE Product
            SET name = %s, category = %s, price = %s, stock_quantity = %s, expiry_date = %s
            WHERE product_id = %s
        """, (name, category, price, stock, expiry, product_id))
        conn.commit()
        cursor.close()
        conn.close()
        return redirect('/products')

    # GET request - fetch product data
    cursor.execute("SELECT * FROM Product WHERE product_id = %s", (product_id,))
    product = cursor.fetchone()
    cursor.close()
    conn.close()
    return render_template('update_product.html', product=product)

# --- Delete Product ---
@app.route('/delete-product/<int:product_id>')
def delete_product(product_id):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Product WHERE product_id = %s", (product_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return redirect('/products')



# --- Run the Flask App ---
if __name__ == "__main__":
    app.run(debug=True, port=5001)
