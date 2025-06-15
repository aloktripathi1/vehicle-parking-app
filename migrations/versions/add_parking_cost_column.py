"""add parking cost column

Revision ID: add_parking_cost_column
Revises: 6891261274ff
Create Date: 2025-06-10 10:32:02.432652

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_parking_cost_column'
down_revision = '6891261274ff'
branch_labels = None
depends_on = None


def upgrade():
    # Add parking_cost column to reservations table
    with op.batch_alter_table('reservations', schema=None) as batch_op:
        batch_op.add_column(sa.Column('parking_cost', sa.Float(), nullable=True))


def downgrade():
    # Remove parking_cost column from reservations table
    with op.batch_alter_table('reservations', schema=None) as batch_op:
        batch_op.drop_column('parking_cost') 