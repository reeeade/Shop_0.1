from flask import Flask, render_template, redirect, session
from flask import request
import sqlite3
from datetime import datetime

import database
import models

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


@app.route('/', methods=['GET'])
def index():
    return redirect('/shop/items')


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
    email = request.form.get('email')
    birthday_str = request.form.get('birthday')
    birthday = datetime.strptime(birthday_str, '%Y-%m-%d')
    database.init_db()
    user = models.User(login=login, password=password, name=name, surname=surname,
                       phone_number=phone_number, email=email, birth_date=birthday)
    database.db_session.add(user)
    database.db_session.commit()
    return redirect('/login')


@app.route('/login', methods=['POST', 'GET'])
def login_user():
    if request.method == 'GET':
        if 'login' in session:
            return redirect('/user')
        return render_template('login.html')
    login = request.form.get('login')
    password = request.form.get('password')
    database.init_db()
    user = models.User.query.filter_by(login=login, password=password).first()
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
    database.init_db()
    item = models.Items.query.filter_by(item_id=item_id).first()
    return render_template('item.html', item=item)


@app.route('/shop/items/<item_id>/review', methods=['GET', 'POST'])
def get_post_review(item_id):
    database.init_db()
    if request.method == 'POST':
        text = request.form.get('text')
        rating = request.form.get('rating')
        user_login = session.get('login')
        if user_login:
            new_feedback = models.Feedback(item_id=item_id, text=text, rating=rating, user_login=user_login)
            database.db_session.add(new_feedback)
            database.db_session.commit()

        return redirect(f'/shop/items/{item_id}')
    else:
        item = models.Items.query.filter_by(item_id=item_id).first()
        return render_template('review.html', item=item)


@app.route('/shop/items/<item_id>/review/<review_id>', methods=['GET', 'POST'])
def get_put_current_review(item_id, review_id):
    if request.method == 'POST':
        update_db('feedback', {'text': request.form.get('text')},
                  {'item_id': item_id, 'feedback_id': review_id})
    return read_from_db('feedback', {"item_id": item_id, "feedback_id": review_id})


@app.route('/shop/items', methods=['GET'])
def get_all_sorted_items():
    user_login = session.get('login')
    user = None
    if user_login:
        user = models.User.query.filter_by(login=user_login).first()
    items = (database.db_session.query(models.Items, models.ItemStatus, models.Category).
             join(models.ItemStatus, models.Items.status_id == models.ItemStatus.status_id).
             join(models.Category, models.Items.category_id == models.Category.category_id))
    categories = models.Category.query.order_by(models.Category.category_name).all()
    statuses = models.ItemStatus.query.order_by(models.ItemStatus.status_name).all()
    query_categories = []
    query_statuses = []
    query_string = request.query_string.decode()
    if query_string:
        query_categories = request.args.getlist('category_name')
        query_statuses = request.args.getlist('status_name')
        if query_categories:
            items = items.filter(models.Category.category_name.in_(query_categories))
        if query_statuses:
            items = items.filter(models.ItemStatus.status_name.in_(query_statuses))
        if request.args.get('min_price'):
            items = items.filter(models.Items.price >= int(request.args.get('min_price')))
        if request.args.get('max_price'):
            items = items.filter(models.Items.price <= int(request.args.get('max_price')))
        if request.args.get('item_name'):
            items = items.filter(models.Items.name.ilike(f'%{request.args.get("item_name")}%'))
    items = items.all()
    items_list = [{**item[0].to_dict(), **item[1].to_dict(), **item[2].to_dict()} for item in items]

    return render_template('items.html', items=items_list, user=user, categories=categories, statuses=statuses,
                           selected_categories=query_categories, selected_statuses=query_statuses,
                           min_price=request.args.get('min_price'), max_price=request.args.get('max_price'),
                           item_name=request.args.get('item_name'))


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
        database.init_db()
        if request.method == 'POST':
            item_id = request.form.get('item_id')
            quantity = request.form.get('quantity')
            item_in_cart = models.Cart.query.filter_by(user_login=current_user, item_id=item_id).first()
            if item_in_cart:
                new_quantity = int(item_in_cart.quantity) + int(quantity)
                item_in_cart.quantity = new_quantity
                database.db_session.commit()
            else:
                new_item_in_cart = models.Cart(quantity=quantity, item_id=item_id, user_login=current_user)
                database.db_session.add(new_item_in_cart)
                database.db_session.commit()
            return redirect('/shop/items')
        else:
            user_cart = (database.db_session.query(models.Cart, models.Items).
                         join(models.Cart, models.Cart.item_id == models.Items.item_id).
                         where(models.Cart.user_login == current_user).all())
            user_cart = [{**item[0].to_dict(), **item[1].to_dict()} for item in user_cart]
            user_info = models.User.query.filter_by(login=current_user).first()
            for item in user_cart:
                item['total_price'] = item['price'] * int(item['quantity'])
            total_cart_amount = sum([item['total_price'] for item in user_cart])
            return render_template('cart.html',
                                   current_user=current_user,
                                   user_cart=user_cart,
                                   user_info=user_info,
                                   total_cart_amount=total_cart_amount)
    else:
        return redirect('/login')


@app.route('/shop/cart/update', methods=['POST'])
def update_cart():
    current_user = session.get('login')
    quantity = request.form.get('quantity')
    item_id = request.form.get('item_id')
    if current_user:
        database.init_db()
        item_in_cart = models.Cart.query.filter_by(user_login=current_user, item_id=item_id).first()
        item_in_cart.quantity = int(quantity)
        database.db_session.commit()
        return redirect('/shop/cart')
    else:
        return redirect('/login')


@app.route('/shop/cart/delete', methods=['POST'])
def delete_cart():
    current_user = session.get('login')
    item_id = request.form.get('item_id')
    if current_user:
        if request.method == 'POST':
            database.init_db()
            deleted_item = models.Cart.query.filter_by(user_login=current_user, item_id=item_id).first()
            database.db_session.delete(deleted_item)
            database.db_session.commit()
        return redirect('/shop/cart')
    else:
        return redirect('/login')


@app.route('/shop/cart/order', methods=['GET', 'POST'])
def get_post_cart_order():
    user_login = session.get('login')
    database.init_db()
    user_cart = (database.db_session.query(models.Cart, models.Items).
                 join(models.Cart, models.Cart.item_id == models.Items.item_id).
                 where(models.Cart.user_login == user_login).all())
    user_cart = [{**item[0].to_dict(), **item[1].to_dict()} for item in user_cart]
    order_total_price = 0
    for item in user_cart:
        order_total_price += int(item['price']) * int(item['quantity'])
    if request.method == 'POST':
        address = request.form.get('address')
        new_order = models.Order(user_login=user_login, address=address, order_total_price=order_total_price, status=1)
        database.db_session.add(new_order)
        database.db_session.commit()
        message = 'Your order has been placed successfully!'
        deleted_cart = models.Cart.query.filter_by(user_login=user_login).all()
        for cart_item in deleted_cart:
            database.db_session.delete(cart_item)
        database.db_session.commit()
        return render_template('cart.html', login=user_login, message2=message)
    else:
        return render_template('order.html', login=user_login,
                               total_price=order_total_price)


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
    database.init_db()
    current_user = models.User.query.filter_by(login=user_login).first()
    return render_template('user_info.html', current_user=current_user)


@app.route('/user', methods=['POST'])
def update_user():
    current_user = session.get('login')
    password = request.form.get('password')
    name = request.form.get('name')
    surname = request.form.get('surname')
    phone_number = request.form.get('phone_number')
    birthday_str = request.form.get('birthday')
    email = request.form.get('email')
    birthday = datetime.strptime(birthday_str, '%Y-%m-%d')
    database.init_db()
    user = models.User.query.filter_by(login=current_user).first()
    user.password = password
    user.name = name
    user.surname = surname
    user.phone_number = phone_number
    user.email = email
    user.birth_date = birthday
    database.db_session.commit()
    return redirect('/user')


@app.route('/user/update', methods=['GET'])
def get_update_user():
    user_login = session.get('login')
    current_user = models.User.query.filter_by(login=user_login).first()
    return render_template('update_user.html', current_user=current_user)


@app.route('/shop/compare/<cmp_id>', methods=["GET", "POST"])
def compare(cmp_id):
    if request.method == 'GET':
        database.init_db()
        compare_items = (database.db_session.query(models.CompareItems, models.Items).
                         filter(models.CompareItems.id == cmp_id).
                         join(models.Items, models.Items.item_id == models.CompareItems.item_id)).all()
        items_list = [{**item[0].to_dict(), **item[1].to_dict()} for item in compare_items]
        return f"This is the comparison with id {cmp_id}"
    else:
        return f"Let's change your comparison with id {cmp_id}"


@app.route('/shop/compare', methods=['POST', 'GET'])
def add_compare():
    login = session.get('login')
    database.init_db()
    if request.method == 'POST':
        item_id = request.form.get('item_id')
        item_with_category = (database.db_session.query(models.Items, models.Category).
                              filter(models.Items.item_id == item_id).
                              join(models.Category, models.Category.category_id == models.Items.category_id)).first()
        category_name = item_with_category[1].category_name
        new_cmp = models.CompareItems(user_login=login, item_id=item_id, name=category_name)
        item_in_cmp = models.CompareItems.query.filter_by(user_login=login, item_id=item_id).first()
        if not item_in_cmp:
            database.db_session.add(new_cmp)
        database.db_session.commit()
        return redirect('/shop/items')
    else:
        user_cmp = (database.db_session.query(models.CompareItems, models.Items, models.Category).
                    filter(models.CompareItems.user_login == session.get('login')).
                    join(models.Items, models.Items.item_id == models.CompareItems.item_id).
                    join(models.Category, models.Category.category_id == models.Items.category_id).
                    distinct(models.Category.category_name)).all()
        user_cmp = [{**item[0].to_dict(), **item[1].to_dict(), **item[2].to_dict()} for item in user_cmp]
        return render_template('compare_list.html', compares=user_cmp)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
