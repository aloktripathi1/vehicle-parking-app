"""add payment columns

Revision ID: add_payment_columns
Revises: add_parking_cost_column
Create Date: 2025-06-10 10:32:02.432652

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_payment_columns'
down_revision = 'add_parking_cost_column'
branch_labels = None
depends_on = None


def upgrade():
    # Add payment-related columns to reservations table
    with op.batch_alter_table('reservations', schema=None) as batch_op:
        batch_op.add_column(sa.Column('payment_status', sa.String(20), nullable=True))
        batch_op.add_column(sa.Column('payment_mode', sa.String(20), nullable=True))
        batch_op.add_column(sa.Column('payment_time', sa.DateTime(), nullable=True))
        batch_op.add_column(sa.Column('force_released', sa.Boolean(), nullable=True, default=False))


def downgrade():
    # Remove payment-related columns from reservations table
    with op.batch_alter_table('reservations', schema=None) as batch_op:
        batch_op.drop_column('payment_status')
        batch_op.drop_column('payment_mode')
        batch_op.drop_column('payment_time')
        batch_op.drop_column('force_released') 