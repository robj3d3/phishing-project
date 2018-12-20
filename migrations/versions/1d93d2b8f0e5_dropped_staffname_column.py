"""Dropped staffname column

Revision ID: 1d93d2b8f0e5
Revises: 0e25a8dfc6d6
Create Date: 2018-11-03 15:00:12.042731

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1d93d2b8f0e5'
down_revision = '0e25a8dfc6d6'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("staff") as batch_op:
        batch_op.drop_column('staffname')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('staff', sa.Column('staff_name', sa.VARCHAR(length=64), nullable=True))
    op.add_column('staff', sa.Column('staffname', sa.VARCHAR(length=64), nullable=True))
    op.create_index('ix_staff_staff_name', 'staff', ['staff_name'], unique=False)
    # ### end Alembic commands ###