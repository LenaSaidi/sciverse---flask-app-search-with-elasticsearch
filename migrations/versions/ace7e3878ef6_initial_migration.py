"""Initial migration

Revision ID: ace7e3878ef6
Revises: 
Create Date: 2023-12-24 16:59:22.540175

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ace7e3878ef6'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('firstName', sa.String(length=100), nullable=True))
        batch_op.add_column(sa.Column('lastName', sa.String(length=100), nullable=True))
        batch_op.add_column(sa.Column('nature', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('role', sa.String(length=50), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_column('role')
        batch_op.drop_column('nature')
        batch_op.drop_column('lastName')
        batch_op.drop_column('firstName')

    # ### end Alembic commands ###
