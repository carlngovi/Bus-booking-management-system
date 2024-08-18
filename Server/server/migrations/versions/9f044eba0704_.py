from alembic import op
import sqlalchemy as sa
from sqlalchemy.engine.reflection import Inspector


# revision identifiers, used by Alembic.
revision = '9f044eba0704'
down_revision = 'a53b2c7a8f8e'
branch_labels = None
depends_on = None


def upgrade():
    # Get the current connection
    conn = op.get_bind()
    inspector = Inspector.from_engine(conn)

    # Check if 'driver_id' column already exists
    columns = [col['name'] for col in inspector.get_columns('buses')]
    if 'driver_id' not in columns:
        # Add the 'driver_id' column if it doesn't exist
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

    # Remove the 'driver_id' column if it exists
    conn = op.get_bind()
    inspector = Inspector.from_engine(conn)
    columns = [col['name'] for col in inspector.get_columns('buses')]
    if 'driver_id' in columns:
        op.drop_column('buses', 'driver_id')
