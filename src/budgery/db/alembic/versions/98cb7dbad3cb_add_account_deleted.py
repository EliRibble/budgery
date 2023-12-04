"""add account.deleted

Revision ID: 98cb7dbad3cb
Revises: 1e2e384663d4
Create Date: 2023-12-03 18:02:52.153700

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '98cb7dbad3cb'
down_revision = '1e2e384663d4'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('account', schema=None) as batch_op:
        batch_op.add_column(sa.Column('deleted', sa.DateTime(), nullable=True))

    with op.batch_alter_table('account_history', schema=None) as batch_op:
        batch_op.add_column(sa.Column('deleted', sa.DateTime(), autoincrement=False, nullable=True))


def downgrade():
    with op.batch_alter_table('account_history', schema=None) as batch_op:
        batch_op.drop_column('deleted')

    with op.batch_alter_table('account', schema=None) as batch_op:
        batch_op.drop_column('deleted')
