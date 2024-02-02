"""filed

Revision ID: 2ec640bd325d
Revises: 0ab52bd9e968
Create Date: 2024-02-01 14:43:04.685426

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2ec640bd325d'
down_revision = '0ab52bd9e968'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('filed', sa.String(length=50), nullable=True))
        batch_op.drop_column('field')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('field', sa.TEXT(), nullable=True))
        batch_op.drop_column('filed')

    # ### end Alembic commands ###