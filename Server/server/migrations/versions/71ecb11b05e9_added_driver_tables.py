"""added driver tables

Revision ID: 71ecb11b05e9
Revises: 0fef16b97eac
Create Date: 2024-08-13 01:30:50.836124

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '71ecb11b05e9'
down_revision = '0fef16b97eac'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('drivers',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('full_name', sa.String(length=80), nullable=False),
    sa.Column('id_number', sa.String(length=20), nullable=False),
    sa.Column('driving_license', sa.String(length=20), nullable=False),
    sa.Column('phone_number', sa.String(length=20), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('driving_license'),
    sa.UniqueConstraint('id_number'),
    sa.UniqueConstraint('phone_number')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('drivers')
    # ### end Alembic commands ###
