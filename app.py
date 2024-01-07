from flask import Flask, render_template, redirect, session
from flask import request
import sqlite3

app = Flask(__name__)
app.secret_key = 'super_secret_key'


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


class DbReader:
    def __enter__(self):
        self.my_db = sqlite3.connect('identifier.sqlite')
        self.my_db.row_factory = dict_factory
        self.my_cursor = self.my_db.cursor()
        return self.my_cursor

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.my_db.commit()
        self.my_db.close()


def read_from_db(table_name, where=None):
    with DbReader() as my_cursor:
        cur_string = f"SELECT * FROM {table_name}"
        if where:
            cur_string += " WHERE "
            conditions = []
            for selector in where.keys():
                conditions.append(f"{selector} = ?")
            cur_string += " AND ".join(conditions)
            my_cursor.execute(cur_string, tuple(where.values()))
        else:
            my_cursor.execute(cur_string)
        return my_cursor.fetchall()


def read_multiple_table(table_names: list, conditions: list, where=None):
    # select * from items
    # join item_status on items.status = item_status.status_id
    # join category on items.category = category.category_id
    with DbReader() as my_cursor:
        cur_string = f"SELECT * FROM {table_names[0]}"
        for one_table in table_names[1:]:
            cur_string += f" JOIN {one_table} ON "
            cur_string += " AND ".join(conditions[table_names.index(one_table) - 1])
        if where:
            cur_string += " WHERE "
            conditions = [f"{column} = ?" for column in where.keys()]
            cur_string += " AND ".join(conditions)
            my_cursor.execute(cur_string, tuple(where.values()))
        else:
            my_cursor.execute(cur_string)

        return my_cursor.fetchall()


def write_to_db(table_name, data):
    with DbReader() as my_cursor:
        cur_string = (f"INSERT INTO {table_name} ({', '.join(data.keys())}) "
                      f"VALUES ({', '.join(['?'] * len(data.keys()))})")
        my_cursor.execute(cur_string, list(data.values()))


def update_db(table_name, data, condition):
    with DbReader() as my_cursor:
        set_clause = ', '.join([f'{key} = ?' for key in data.keys()])
        where_clause = ' AND '.join([f'{key} = ?' for key in condition.keys()])
        cur_string = f"UPDATE {table_name} SET {set_clause} WHERE {where_clause}"
        set_values = list(data.values())
        where_values = list(condition.values())
        query_values = set_values + where_values
        my_cursor.execute(cur_string, query_values)


def delete_from_db(table_name, condition):
    with DbReader() as my_cursor:
        cur_string = f"DELETE FROM {table_name} WHERE {' AND '.join([f'{key} = ?' for key in condition.keys()])}"
        my_cursor.execute(cur_string, list(condition.values()))


@app.route('/register', methods=['POST', 'GET'])
def register_user():
    if request.method == 'GET':
        if 'login' in session:
            return redirect('/user')
        return render_template('register.html')
    login = request.form.get('login')
    password = request.form.get('password')
    name = request.form.get('name')
    surname = request.form.get('surname')
    phone_number = request.form.get('phone_number')
    write_to_db('users', {'login': login, 'password': password,
                          'name': name, 'surname': surname, 'phone_number': phone_number})
    return redirect('/login')


@app.route('/login', methods=['POST', 'GET'])
def login_user():
    if request.method == 'GET':
        if 'login' in session:
            return redirect('/user')
        return render_template('login.html')
    login = request.form.get('login')
    password = request.form.get('password')
    user = read_from_db('users', {'login': login, 'password': password})
    if user:
        session['login'] = login
        return redirect('/user')
    else:
        return render_template('login.html', error='Incorrect login or password')


@app.route('/logout', methods=['GET'])
def logout_user():
    session.pop('login', None)
    return redirect('/login')


@app.route('/shop/items/<item_id>', methods=['GET'])
def get_items(item_id):
    return read_from_db('items', {'item_id': item_id})


@app.route('/shop/items/<item_id>/review', methods=['GET', 'POST'])
def get_post_review(item_id):
    if request.method == 'POST':
        write_to_db('feedback', {'item_id': item_id, 'text': request.form.get('text'),
                                 'rating': request.form.get('rating'), 'user_login': request.form.get('user_login')})
    return read_from_db('feedback', {'item_id': item_id})


@app.route('/shop/items/<item_id>/review/<review_id>', methods=['GET', 'PUT'])
def get_put_current_review(item_id, review_id):
    if request.method == 'PUT':
        update_db('feedback', {'text': request.form.get('text')},
                  {'item_id': item_id, 'feedback_id': review_id})
    return read_from_db('feedback', {"item_id": item_id, "feedback_id": review_id})


@app.route('/shop/items', methods=['GET'])
def get_all_sorted_items():
    user_login = session.get('login')
    user = None
    if user_login:
        user = read_from_db('users', {'login': user_login})[0]
    items = read_multiple_table(['items', 'item_status', 'category'],
                                [('items.status_id = item_status.status_id',),
                                 ('items.category_id = category.category_id',)])
    return render_template('items.html', items=items, user=user)


@app.route('/shop/search', methods=['POST'])
def search_items():
    item_name = request.form.get('item_name')
    item = read_from_db('items', {'name': item_name})
    if item:
        return item
    else:
        return 'Item not found'


@app.route('/shop/cart', methods=['POST', 'GET'])
def add_cart():
    current_user = session.get('login')
    if current_user:
        if request.method == 'POST':
            item_id = request.form.get('item_id')
            quantity = request.form.get('quantity')
            item_in_cart = read_from_db('cart', {'item_id': item_id, 'user_login': current_user})
            if item_in_cart:
                new_quantity = int(item_in_cart[0]['quantity']) + int(quantity)
                update_db('cart', {'quantity': new_quantity},
                          {'item_id': item_id, 'user_login': current_user})
            else:
                write_to_db('cart', {'item_id': item_id,
                                     'quantity': quantity,
                                     'user_login': current_user})
        user_cart = read_multiple_table(['cart', 'items'],
                                        [('cart.item_id = items.item_id',)],
                                        {'user_login': current_user})
        user_info = read_from_db('users', {'login': current_user})[0]
        for item in user_cart:
            item['total_price'] = item['price'] * int(item['quantity'])
        return render_template('cart.html',
                               current_user=current_user,
                               user_cart=user_cart,
                               user_info=user_info)
    else:
        return redirect('/login')


@app.route('/shop/cart/update', methods=['POST'])
def update_cart():
    current_user = session.get('login')
    if current_user:
        update_db('cart',
                  {'quantity': request.form.get('quantity')},
                  {'item_id': request.form.get('item_id'), 'user_login': current_user})
        return redirect('/shop/cart')
    else:
        return redirect('/login')


@app.route('/shop/cart/delete', methods=['POST'])
def delete_cart():
    current_user = session.get('login')
    if current_user:
        if request.method == 'POST':
            delete_from_db('cart', {'item_id': request.form.get('item_id'),
                                    'user_login': current_user})
        return redirect('/shop/cart')
    else:
        return redirect('/login')


@app.route('/shop/cart/order', methods=['GET', 'POST'])
def get_post_cart_order():
    user_login = request.form.get('user_login')
    address = request.form.get('address')
    order_total_price = request.form.get('order_total_price')
    status = request.form.get('status')
    if request.method == 'GET':
        return 'This is the order form!'
    else:
        write_to_db('orders', {'user_login': user_login, 'address': address,
                               'order_total_price': order_total_price, 'status': status})
    return read_from_db('orders')


@app.route('/shop/favorites/<list_id>', methods=['GET', 'PUT'])
def get_put_favorites(list_id):
    if request.method == 'PUT':
        update_db('wishlist', {'list_name': request.form.get('list_name')},
                  {'list_id': list_id})
    return read_from_db('wishlist', {'list_id': list_id})


@app.route('/shop/favorites', methods=['POST'])
def add_favorites():
    write_to_db('wishlist', {'list_name': request.form.get('list_name'),
                             'user_login': request.form.get('user_login'), 'item_id': request.form.get('item_id')})
    return read_from_db('wishlist')


@app.route('/shop/waitlist', methods=['GET', 'PUT'])
def get_put_waitlist():
    if request.method == 'PUT':
        update_db('waitlist', {'item_id': request.form.get('item_id')},
                  {'user_login': request.form.get('user_login')})
    return read_from_db('waitlist')


@app.route('/admin/items', methods=['GET', 'POST'])
def get_add_admin_items():
    if request.method == 'POST':
        write_to_db('items', {'name': request.form.get('name'),
                              'description': request.form.get('description'),
                              'price': request.form.get('price'),
                              'status': request.form.get('status'),
                              'category': request.form.get('category')})
    return read_from_db('items')


@app.route('/admin/items/<item_id>', methods=['GET', 'PUT', 'DELETE'])
def get_put_delete_admin_items(item_id):
    if request.method == 'PUT':
        update_db('items', {'name': request.form.get('name'),
                            'description': request.form.get('description'),
                            'price': request.form.get('price'),
                            'status': request.form.get('status'),
                            'category': request.form.get('category')},
                  {item_id: request.form.get('item_id')})
    elif request.method == 'DELETE':
        delete_from_db('items', {'item_id': item_id})
    return read_from_db('items')


@app.route('/admin/orders', methods=['GET'])
def get_admin_orders():
    return read_from_db('orders')


@app.route('/admin/orders/<order_id>', methods=['PUT'])
def update_order(order_id):
    update_db('orders', {'status': request.form.get('status')}, {'order_id': order_id})
    return read_from_db('orders')


@app.route('/admin/stat', methods=['GET'])
def get_admin_stat():
    return 'This is the admin stat!'


@app.route('/user', methods=['GET'])
def get_user():
    user_login = session.get('login')
    current_user = read_from_db('users', {'login': user_login})[0]
    return render_template('user_info.html', current_user=current_user)


@app.route('/user', methods=['POST'])
def update_user():
    update_db('users', {'password': request.form.get('password'),
                        'name': request.form.get('name'),
                        'surname': request.form.get('surname'),
                        'phone_number': request.form.get('phone_number')},
              {'login': session.get('login')})
    return redirect('/user')


@app.route('/user/update', methods=['GET'])
def get_update_user():
    user_login = session.get('login')
    current_user = read_from_db('users', {'login': user_login})[0]
    return render_template('update_user.html', current_user=current_user)


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
