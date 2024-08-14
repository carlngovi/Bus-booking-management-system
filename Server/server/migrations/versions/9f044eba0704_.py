"""empty message

Revision ID: 9f044eba0704
Revises: a53b2c7a8f8e
Create Date: 2024-08-14 09:29:55.627332

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9f044eba0704'
down_revision = 'a53b2c7a8f8e'
branch_labels = None
depends_on = None


def upgrade():
    # Add the 'driver_id' column
    op.add_column('buses', sa.Column('driver_id', sa.Integer(), nullable=True))

    # Create a foreign key constraint
    op.create_foreign_key(
        'fk_buses_driver_id',  # Constraint name
        'buses',               # Source table
        'drivers',             # Target table
        ['driver_id'],         # Source column(s)
        ['id']                 # Target column(s)
    )

def downgrade():
    # Drop the foreign key constraint
    op.drop_constraint('fk_buses_driver_id', 'buses', type_='foreignkey')

    # Remove the 'driver_id' column
    op.drop_column('buses', 'driver_id')