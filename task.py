from celery import Celery
import os
import smtplib
from email.mime.text import MIMEText
import database
import models

broker_host = os.environ.get('RABBIT_HOST', 'localhost')
app = Celery('tasks', broker=f'pyamqp://guest@{broker_host}//')


@app.task
def send_email(login, order_id):
    database.init_db()
    user_object = models.User.query.filter_by(login=login).first()
    email = user_object.email
    order_object = models.Order.query.filter_by(order_id=order_id).first()
    order_items = (database.db_session.query(models.OrderItem, models.Items).
                   filter(models.OrderItem.order_id == order_id).
                   join(models.Items, models.Items.item_id == models.OrderItem.item_id)).all()
    item_list = ((item[1].name, item[0].quantity) for item in order_items)
    message = f'Заказ №{order_object.order_id} от {user_object.login}:\n'
    for item in item_list:
        message += f'{item[0]} x {item[1]}\n'
    message += f'Сумма заказа: {order_object.order_total_price}'

    sender = os.environ.get('EMAIL_USER')
    password = os.environ.get('EMAIL_PASS')

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()

    server.login(sender, password)
    msg = MIMEText(message)
    msg['From'] = f'{sender}'
    msg['Subject'] = f'Заказ №{order_object.order_id}'
    server.sendmail(sender, email, msg.as_string())
