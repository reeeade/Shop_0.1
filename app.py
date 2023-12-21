from flask import Flask
from flask import request
import sqlite3

app = Flask(__name__)


@app.route('/register', methods=['POST'])
def register_user():
    return 'Hello, user!'


@app.route('/login', methods=['POST'])
def login_user():
    return 'Welcome back, user!'


@app.route('/shop/items/<item_id>', methods=['GET'])
def get_items(item_id):
    my_db = sqlite3.connect('identifier.sqlite')
    my_cursor = my_db.cursor()
    my_cursor.execute("SELECT * FROM items WHERE item_id = ?", (item_id,))
    items = my_cursor.fetchall()
    my_db.close()
    return items


@app.route('/shop/items/<item_id>/review', methods=['GET', 'POST'])
def get_post_review(item_id):
    if request.method == 'POST':
        return f'Ok, lets post your review for {item_id}!'
    else:
        my_db = sqlite3.connect('identifier.sqlite')
        my_cursor = my_db.cursor()
        my_cursor.execute("SELECT * FROM feedback WHERE item_id = ?", (item_id,))
        feedback = my_cursor.fetchall()
        my_db.close()
        return feedback


@app.route('/shop/items/<item_id>/review/<review_id>', methods=['GET', 'PUT'])
def get_put_current_review(item_id, review_id):
    if request.method == 'PUT':
        return f'Ok, lets put your review for {item_id} and {review_id}!'
    else:
        my_db = sqlite3.connect('identifier.sqlite')
        my_cursor = my_db.cursor()
        my_cursor.execute("SELECT * FROM feedback WHERE item_id = ? and feedback_id = ?", (item_id,
                                                                                           review_id))
        feedback = my_cursor.fetchall()
        my_db.close()
        return feedback


@app.route('/shop/items', methods=['GET'])
def get_all_sorted_items():
    category = request.args.get('category')
    order = request.args.get('order')
    page = request.args.get('page')
    my_db = sqlite3.connect('identifier.sqlite')
    my_cursor = my_db.cursor()
    my_cursor.execute(f"SELECT * FROM items WHERE category = ? ORDER BY {order} DESC ", (category,))
    items = my_cursor.fetchall()
    my_db.close()
    return items


@app.route('/shop/search', methods=['POST'])
def search_items():
    return 'This is the all items you are searching for!'


@app.route('/shop/cart', methods=['GET'])
def get_cart():
    my_db = sqlite3.connect('identifier.sqlite')
    my_cursor = my_db.cursor()
    my_cursor.execute("SELECT * FROM cart")
    cart = my_cursor.fetchall()
    my_db.close()
    return cart


@app.route('/shop/cart', methods=['POST', 'PUT'])
def add_cart():
    item_id = request.args.get('item_id')
    amount = request.args.get('amount')
    if request.method == 'POST':
        return f'Ok, lets add in cart item {item_id}!'
    else:
        return f'Ok, lets put amount {amount}!'


@app.route('/shop/cart', methods=['DELETE'])
def delete_cart():
    item_id = request.args.get('item_id')
    return f'Ok, lets delete cart item {item_id}'


@app.route('/shop/cart/order', methods=['GET', 'POST'])
def get_post_cart_order():
    if request.method == 'GET':
        return 'This is the order form!'
    else:
        return "Let's place your order!"


@app.route('/shop/favorites/<list_id>', methods=['GET', 'PUT'])
def get_put_favorites(list_id):
    if request.method == 'GET':
        my_db = sqlite3.connect('identifier.sqlite')
        my_cursor = my_db.cursor()
        my_cursor.execute("SELECT * FROM wishlist WHERE list_id = ?", (list_id,))
        wishlist = my_cursor.fetchall()
        my_db.close()
        return wishlist
    else:
        return f"Let's change your favorite list with id {list_id}!"


@app.route('/shop/favorites', methods=['POST'])
def add_favorites():
    return "Let's add your favorites!"


@app.route('/shop/waitlist', methods=['GET', 'PUT'])
def get_put_waitlist():
    if request.method == 'GET':
        my_db = sqlite3.connect('identifier.sqlite')
        my_cursor = my_db.cursor()
        my_cursor.execute("SELECT * FROM waitlist")
        waitlist = my_cursor.fetchall()
        my_db.close()
        return waitlist
    else:
        return "Let's change your waitlist!"


@app.route('/admin/items', methods=['GET', 'POST'])
def get_add_admin_items():
    if request.method == 'GET':
        my_db = sqlite3.connect('identifier.sqlite')
        my_cursor = my_db.cursor()
        my_cursor.execute("SELECT * FROM items")
        items = my_cursor.fetchall()
        my_db.close()
        return items
    else:
        return "Let's add new items"


@app.route('/admin/items/<item_id>', methods=['GET', 'PUT', 'DELETE'])
def get_put_delete_admin_items(item_id):
    if request.method == 'GET':
        my_db = sqlite3.connect('identifier.sqlite')
        my_cursor = my_db.cursor()
        my_cursor.execute("SELECT * FROM items WHERE item_id = ?", (item_id,))
        items = my_cursor.fetchall()
        my_db.close()
        return items
    elif request.method == 'PUT':
        return f"Let's update item with id {item_id}"
    else:
        return f"Let's delete item with id {item_id}"


@app.route('/admin/orders', methods=['GET'])
def get_admin_orders():
    return 'These are orders for the administrator!'


@app.route('/admin/orders/<order_id>', methods=['PUT'])
def update_order(order_id):
    return f"Let's update order with id {order_id}"


@app.route('/admin/stat', methods=['GET'])
def get_admin_stat():
    return 'This is the admin stat!'


@app.route('/user', methods=['PUT'])
def update_user():
    return "Let's update user information!"


@app.route('/shop/compare/<cmp_id>', methods=["GET", "PUT"])
def compare(cmp_id):
    if request.method == 'GET':
        return f"This is the comparison with id {cmp_id}"
    else:
        return f"Let's change your comparison with id {cmp_id}"


@app.route('/shop/compare', methods=['POST'])
def add_compare():
    return f"Let's add comparison"


if __name__ == '__main__':
    app.run()
