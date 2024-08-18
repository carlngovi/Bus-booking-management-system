from alembic import op
import sqlalchemy as sa
from sqlalchemy.engine.reflection import Inspector


# revision identifiers, used by Alembic.
revision = 'fd847801fc78'
down_revision = '9f044eba0704'
branch_labels = None
depends_on = None


def upgrade():
    # Get the current connection
    conn = op.get_bind()
    inspector = Inspector.from_engine(conn)

    # Check if 'driver_id' column already exists in 'buses'
    columns = [col['name'] for col in inspector.get_columns('buses')]
    
    with op.batch_alter_table('buses', schema=None) as batch_op:
        if 'driver_id' not in columns:
            # Add the 'driver_id' column if it doesn't exist
            batch_op.add_column(sa.Column('driver_id', sa.Integer(), nullable=False))
            # Create the foreign key constraint
            batch_op.create_foreign_key(batch_op.f('fk_buses_driver_id_drivers'), 'drivers', ['driver_id'], ['id'])

        # Add 'departure_from' and 'departure_to' columns
        batch_op.add_column(sa.Column('departure_from', sa.String(length=20), nullable=False))
        batch_op.add_column(sa.Column('departure_to', sa.String(length=20), nullable=False))
        
        # Drop the misspelled columns if they exist
        if 'depatrture_from' in columns:
            batch_op.drop_column('depatrture_from')
        if 'depatrture_to' in columns:
            batch_op.drop_column('depatrture_to')
        
        # Drop the 'driver_full_name' column if it exists
        if 'driver_full_name' in columns:
            batch_op.drop_column('driver_full_name')


def downgrade():
    # Get the current connection
    conn = op.get_bind()
    inspector = Inspector.from_engine(conn)

    # Check if columns exist before dropping them
    columns = [col['name'] for col in inspector.get_columns('buses')]
    
    with op.batch_alter_table('buses', schema=None) as batch_op:
        # Re-add dropped columns
        if 'driver_full_name' not in columns:
            batch_op.add_column(sa.Column('driver_full_name', sa.VARCHAR(length=80), autoincrement=False, nullable=False))
        if 'depatrture_to' not in columns:
            batch_op.add_column(sa.Column('depatrture_to', sa.VARCHAR(length=20), autoincrement=False, nullable=False))
        if 'depatrture_from' not in columns:
            batch_op.add_column(sa.Column('depatrture_from', sa.VARCHAR(length=20), autoincrement=False, nullable=False))
        
        # Drop foreign key constraint if it exists
        batch_op.drop_constraint(batch_op.f('fk_buses_driver_id_drivers'), type_='foreignkey')
        
        # Drop added columns
        if 'departure_to' in columns:
            batch_op.drop_column('departure_to')
        if 'departure_from' in columns:
            batch_op.drop_column('departure_from')
        if 'driver_id' in columns:
            batch_op.drop_column('driver_id')
