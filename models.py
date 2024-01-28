from sqlalchemy import Column, Integer, String, ForeignKey, Date
from database import Base


class User(Base):
    __tablename__ = 'users'
    login = Column(String(32), primary_key=True, nullable=False)
    password = Column(String(32), nullable=False)
    name = Column(String(32), nullable=False)
    surname = Column(String(32), nullable=False)
    phone_number = Column(String(32), nullable=False)
    email = Column(String(32), nullable=True)
    birth_date = Column(Date, nullable=True)

    def to_dict(self):
        return {
            'login': self.login,
            'password': self.password,
            'name': self.name,
            'surname': self.surname,
            'phone_number': self.phone_number
        }

    def __repr__(self):
        return self.to_dict()


class Items(Base):
    __tablename__ = 'items'
    item_id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    name = Column(String(32), nullable=False)
    description = Column(String(100))
    price = Column(Integer, nullable=False)
    status_id = Column(Integer, ForeignKey('item_status.status_id'), nullable=False)
    category_id = Column(Integer, ForeignKey('category.category_id'), nullable=False)

    def to_dict(self):
        return {
            'item_id': self.item_id,
            'name': self.name,
            'description': self.description,
            'price': self.price,
            'status_id': self.status_id,
            'category_id': self.category_id
        }

    def __repr__(self):
        return self.to_dict()


class Cart(Base):
    __tablename__ = 'cart'
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    user_login = Column(String(32), ForeignKey('users.login'), nullable=False)
    item_id = Column(Integer, ForeignKey('items.item_id'), nullable=False)
    quantity = Column(Integer, nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'user_login': self.user_login,
            'item_id': self.item_id,
            'quantity': self.quantity
        }

    def __repr__(self):
        return self.to_dict()


class Feedback(Base):
    __tablename__ = 'feedback'
    feedback_id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    item_id = Column(Integer, ForeignKey('items.item_id'), nullable=False)
    text = Column(String(200))
    rating = Column(Integer, nullable=False)
    user_login = Column(String(32), ForeignKey('users.login'), nullable=False)

    def to_dict(self):
        return {
            'feedback_id': self.feedback_id,
            'item_id': self.item_id,
            'text': self.text,
            'rating': self.rating,
            'user_login': self.user_login
        }

    def __repr__(self):
        return self.to_dict()


class Order(Base):
    __tablename__ = 'orders'
    order_id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    user_login = Column(String(32), ForeignKey('users.login'), nullable=False)
    address = Column(String(100), nullable=False)
    order_total_price = Column(Integer, nullable=False)
    status = Column(Integer, ForeignKey('order_status.status_id'), nullable=False)

    def to_dict(self):
        return {
            'order_id': self.order_id,
            'user_login': self.user_login,
            'address': self.address,
            'order_total_price': self.order_total_price,
            'status': self.status
        }

    def __repr__(self):
        return self.to_dict()


class Wishlist(Base):
    __tablename__ = 'wishlist'
    list_id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    list_name = Column(String(32), nullable=False)
    user_login = Column(String(32), ForeignKey('users.login'), nullable=False)
    item_id = Column(Integer, ForeignKey('items.item_id'), nullable=False)

    def to_dict(self):
        return {
            'list_id': self.list_id,
            'list_name': self.list_name,
            'user_login': self.user_login,
            'item_id': self.item_id
        }

    def __repr__(self):
        return self.to_dict()


class Category(Base):
    __tablename__ = 'category'
    category_id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    category_name = Column(String(32), nullable=False)

    def to_dict(self):
        return {
            'category_id': self.category_id,
            'category_name': self.category_name
        }

    def __repr__(self):
        return self.to_dict()


class ItemStatus(Base):
    __tablename__ = 'item_status'
    status_id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    status_name = Column(String(32), nullable=False)

    def to_dict(self):
        return {
            'status_id': self.status_id,
            'status_name': self.status_name
        }

    def __repr__(self):
        return self.to_dict()


class OrderStatus(Base):
    __tablename__ = 'order_status'
    status_id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    status_name = Column(String(32), nullable=False)

    def to_dict(self):
        return {
            'status_id': self.status_id,
            'status_name': self.status_name
        }

    def __repr__(self):
        return self.to_dict()


class Waitlist(Base):
    __tablename__ = 'waitlist'
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    user_login = Column(String(32), ForeignKey('users.login'), nullable=False)
    item_id = Column(Integer, ForeignKey('items.item_id'), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'user_login': self.user_login,
            'item_id': self.item_id
        }

    def __repr__(self):
        return self.to_dict()


class OrderItem(Base):
    __tablename__ = 'order_items'
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    order_id = Column(Integer, ForeignKey('orders.order_id'), nullable=False)
    item_id = Column(Integer, ForeignKey('items.item_id'), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'order_id': self.order_id,
            'item_id': self.item_id
        }

    def __repr__(self):
        return self.to_dict()


class CompareItems(Base):
    __tablename__ = 'compare_items'
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    name = Column(String(32), nullable=False)
    user_login = Column(String(32), ForeignKey('users.login'), nullable=False)
    item_id = Column(Integer, ForeignKey('items.item_id'), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'user_login': self.user_login,
            'item_id': self.item_id
        }

