# inventory_manager.py

import json
import os
from typing import List, Optional

INVENTORYFILE = 'inventory_data.json'
LOW_STOCKTHRESHOLD = 10

class Product:
    """Represents a product in the inventory."""
    def __init__(self, name: str, price: float, stock: int, item_code: str):
        self.name = name
        self.price = price
        self.stock = stock
        self.item_code = item_code

    def __str__(self):
        return f"Code: {self.item_code:<6} | Name: {self.name:<20} | Price: Rs{self.price:7.2f} | Stock: {self.stock:>5}"

    def to_dict(self):
        return {
            "name": self.name,
            "price": self.price,
            "stock": self.stock,
            "item_code": self.item_code
        }

def load_inventory() -> List[Product]:
    """Loads inventory data from the JSON file."""
    if not os.path.exists(INVENTORYFILE):
        return []
    
    try:
        with open(INVENTORYFILE, 'r') as f:
            data = json.load(f)
            return [Product(
                name=item['name'], 
                price=item['price'], 
                stock=int(item['stock']), 
                item_code=item['item_code']
            ) for item in data]
    except (IOError, json.JSONDecodeError, KeyError, ValueError) as e:
        print(f"Warning: Could not read {INVENTORYFILE}. Starting with an empty inventory. Error: {e}") 
        return []

def save_inventory(inventory: List[Product]):
    """Saves the current inventory to the JSON file."""
    data = [product.to_dict() for product in inventory]
    
    try:
        with open(INVENTORYFILE, 'w') as f:
            json.dump(data, f, indent=4)
    except IOError:
        print("Error: Could not save inventory file.")

def generate_item_code(inventory: List[Product]) -> str:
    """Generates a unique item code (ITM001, ITM002, etc.)."""
    if not inventory:
        return "ITM001"
    
    codes = [int(p.item_code[3:]) for p in inventory if p.item_code.startswith("ITM")]
    new_num = max(codes) + 1 if codes else 1
    return f"ITM{new_num:03d}"

# --- Business Logic Functions ---

def find_product(inventory: List[Product], item_code: str) -> Optional[Product]:
    """Finds a product by item code."""
    return next((p for p in inventory if p.item_code == item_code.upper().strip()), None)

def get_product_by_name(inventory: List[Product], name: str) -> Optional[Product]:
    """Finds a product by name (case-insensitive)."""
    return next((p for p in inventory if p.name.lower() == name.lower()), None)

def add_product(inventory: List[Product], name: str, price: float, stock: int) -> Optional[Product]:
    """Adds a new product to the inventory. Returns the new Product object or None on failure."""
    
    if price <= 0 or stock < 0:
        return None
    
    if get_product_by_name(inventory, name):
        return None
        
    item_code = generate_item_code(inventory)
    new_product = Product(name, price, stock, item_code) 
    inventory.append(new_product)
    
    return new_product

def update_product_details(inventory: List[Product], item_code: str, new_stock: Optional[int] = None, new_price: Optional[float] = None) -> bool:
    """Updates the stock and/or price of an existing product."""
    product = find_product(inventory, item_code)
    
    if not product:
        return False
        
    if new_stock is not None:
        if new_stock < 0: return False
        product.stock = new_stock
        
    if new_price is not None:
        if new_price <= 0: return False
        product.price = new_price
        
    return True

def delete_product(inventory: List[Product], item_code: str) -> bool:
    """Removes a product from the inventory based on item code."""
    product = find_product(inventory, item_code)
    if product:
        inventory.remove(product)
        return True
    return False

def get_low_stock_items(inventory: List[Product]) -> List[Product]:
    """Returns a list of products below the LOW_STOCKTHRESHOLD."""
    return [p for p in inventory if p.stock < LOW_STOCKTHRESHOLD]

def get_total_inventory_value(inventory: List[Product]) -> float:
    """Calculates the total monetary value of the current inventory."""
    return sum(p.price * p.stock for p in inventory)