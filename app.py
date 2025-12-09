from flask import Flask, render_template, request, redirect, url_for, flash
import inventory_manager
from inventory_manager import load_inventory

app = Flask(__name__)
# IMPORTANT: This secret key is needed for flash messages to work.
app.secret_key = 'Ritika@123' 

# Load inventory once when the app starts
inventory = inventory_manager.load_inventory()

@app.route('/')
def index():
    """Main page showing the full inventory and summary metrics."""
    sorted_inventory = sorted(inventory, key=lambda p: p.item_code)
    total_value = inventory_manager.get_total_inventory_value(inventory)
    low_stock = inventory_manager.get_low_stock_items(inventory)
    
    return render_template(
        'index.html',
        products=sorted_inventory,
        total_value=total_value,
        low_stock_count=len(low_stock),
        inventory_manager=inventory_manager
    )

@app.route('/add', methods=['GET', 'POST'])
def add_product_route():
    """Handles adding a new product via a form."""
    if request.method == 'POST':
        try:
            name = request.form['name'].strip()
            price = float(request.form['price'])
            stock = int(request.form['stock'])
            
            new_product = inventory_manager.add_product(inventory, name, price, stock)
            
            if new_product:
                inventory_manager.save_inventory(inventory)
                flash(f'Product {new_product.item_code} added successfully!', 'success')
                return redirect(url_for('index'))
            else:
                flash('Error: Product name might be a duplicate, or price/stock is invalid.', 'danger')
                
        except ValueError:
            flash('Error: Invalid number format for price or stock.', 'danger')
        except Exception as e:
            flash(f'An unexpected error occurred: {e}', 'danger')

    return render_template('add.html')

@app.route('/update/<item_code>', methods=['GET', 'POST'])
def update_product_route(item_code):
    """Handles updating stock/price for a specific product."""
    product = inventory_manager.find_product(inventory, item_code)
    
    if not product:
        flash(f'Product {item_code} not found.', 'danger')
        return redirect(url_for('index'))

    if request.method == 'POST':
        try:
            new_stock_input = request.form.get('stock').strip()
            stock_value = int(new_stock_input) if new_stock_input else None
            
            new_price_input = request.form.get('price').strip()
            price_value = float(new_price_input) if new_price_input else None

            if inventory_manager.update_product_details(inventory, item_code, stock_value, price_value):
                inventory_manager.save_inventory(inventory)
                flash(f'Product {item_code} updated successfully!', 'success')
            else:
                flash('Error: New stock or price value is invalid.', 'danger')

            return redirect(url_for('index'))

        except ValueError:
            flash('Error: Invalid number format for stock or price.', 'danger')
        
    return render_template('update.html', product=product)

@app.route('/delete/<item_code>')
def delete_product_route(item_code):
    """Deletes a product and redirects to the index page."""
    if inventory_manager.delete_product(inventory, item_code):
        inventory_manager.save_inventory(inventory)
        flash(f'Product {item_code} deleted successfully!', 'warning')
    else:
        flash(f'Error: Product {item_code} not found.', 'danger')
        
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)