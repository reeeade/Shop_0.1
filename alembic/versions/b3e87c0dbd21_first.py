"""first

Revision ID: b3e87c0dbd21
Revises: 
Create Date: 2024-01-09 12:26:55.731272

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'b3e87c0dbd21'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('category',
                    sa.Column('category_id', sa.Integer(), autoincrement=True, nullable=False),
                    sa.Column('category_name', sa.String(length=32), nullable=False),
                    sa.PrimaryKeyConstraint('category_id')
                    )
    op.create_table('item_status',
                    sa.Column('status_id', sa.Integer(), autoincrement=True, nullable=False),
                    sa.Column('status_name', sa.String(length=32), nullable=False),
                    sa.PrimaryKeyConstraint('status_id')
                    )
    op.create_table('order_status',
                    sa.Column('status_id', sa.Integer(), autoincrement=True, nullable=False),
                    sa.Column('status_name', sa.String(length=32), nullable=False),
                    sa.PrimaryKeyConstraint('status_id')
                    )
    op.create_table('users',
                    sa.Column('login', sa.String(length=32), nullable=False),
                    sa.Column('password', sa.String(length=32), nullable=False),
                    sa.Column('name', sa.String(length=32), nullable=False),
                    sa.Column('surname', sa.String(length=32), nullable=False),
                    sa.Column('phone_number', sa.String(length=32), nullable=False),
                    sa.PrimaryKeyConstraint('login')
                    )
    op.create_table('items',
                    sa.Column('item_id', sa.Integer(), autoincrement=True, nullable=False),
                    sa.Column('name', sa.String(length=32), nullable=False),
                    sa.Column('description', sa.String(length=100), nullable=True),
                    sa.Column('price', sa.Integer(), nullable=False),
                    sa.Column('status_id', sa.Integer(), nullable=False),
                    sa.Column('category_id', sa.Integer(), nullable=False),
                    sa.ForeignKeyConstraint(['category_id'], ['category.category_id'], ),
                    sa.ForeignKeyConstraint(['status_id'], ['item_status.status_id'], ),
                    sa.PrimaryKeyConstraint('item_id')
                    )
    op.create_table('orders',
                    sa.Column('order_id', sa.Integer(), autoincrement=True, nullable=False),
                    sa.Column('user_login', sa.String(length=32), nullable=False),
                    sa.Column('address', sa.String(length=100), nullable=False),
                    sa.Column('order_total_price', sa.Integer(), nullable=False),
                    sa.Column('status', sa.Integer(), nullable=False),
                    sa.ForeignKeyConstraint(['status'], ['order_status.status_id'], ),
                    sa.ForeignKeyConstraint(['user_login'], ['users.login'], ),
                    sa.PrimaryKeyConstraint('order_id')
                    )
    op.create_table('cart',
                    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
                    sa.Column('user_login', sa.String(length=32), nullable=False),
                    sa.Column('item_id', sa.Integer(), nullable=False),
                    sa.Column('quantity', sa.Integer(), nullable=False),
                    sa.ForeignKeyConstraint(['item_id'], ['items.item_id'], ),
                    sa.ForeignKeyConstraint(['user_login'], ['users.login'], ),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_table('feedback',
                    sa.Column('feedback_id', sa.Integer(), autoincrement=True, nullable=False),
                    sa.Column('item_id', sa.Integer(), nullable=False),
                    sa.Column('text', sa.String(length=200), nullable=True),
                    sa.Column('rating', sa.Integer(), nullable=False),
                    sa.Column('user_login', sa.String(length=32), nullable=False),
                    sa.ForeignKeyConstraint(['item_id'], ['items.item_id'], ),
                    sa.ForeignKeyConstraint(['user_login'], ['users.login'], ),
                    sa.PrimaryKeyConstraint('feedback_id')
                    )
    op.create_table('order_items',
                    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
                    sa.Column('order_id', sa.Integer(), nullable=False),
                    sa.Column('item_id', sa.Integer(), nullable=False),
                    sa.ForeignKeyConstraint(['item_id'], ['items.item_id'], ),
                    sa.ForeignKeyConstraint(['order_id'], ['orders.order_id'], ),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_table('waitlist',
                    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
                    sa.Column('user_login', sa.String(length=32), nullable=False),
                    sa.Column('item_id', sa.Integer(), nullable=False),
                    sa.ForeignKeyConstraint(['item_id'], ['items.item_id'], ),
                    sa.ForeignKeyConstraint(['user_login'], ['users.login'], ),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_table('wishlist',
                    sa.Column('list_id', sa.Integer(), autoincrement=True, nullable=False),
                    sa.Column('list_name', sa.String(length=32), nullable=False),
                    sa.Column('user_login', sa.String(length=32), nullable=False),
                    sa.Column('item_id', sa.Integer(), nullable=False),
                    sa.ForeignKeyConstraint(['item_id'], ['items.item_id'], ),
                    sa.ForeignKeyConstraint(['user_login'], ['users.login'], ),
                    sa.PrimaryKeyConstraint('list_id')
                    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('wishlist')
    op.drop_table('waitlist')
    op.drop_table('order_items')
    op.drop_table('feedback')
    op.drop_table('cart')
    op.drop_table('orders')
    op.drop_table('items')
    op.drop_table('users')
    op.drop_table('order_status')
    op.drop_table('item_status')
    op.drop_table('category')
    # ### end Alembic commands ###
