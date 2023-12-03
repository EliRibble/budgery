"""move transaction.budget_entry

Revision ID: 1e2e384663d4
Revises: a248e26bd2bb
Create Date: 2023-12-02 15:49:34.162978

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1e2e384663d4'
down_revision = 'a248e26bd2bb'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('transaction', schema=None) as batch_op:
        batch_op.alter_column('budget_entry', new_column_name="budget_entry_id")


def downgrade():
    with op.batch_alter_table('transaction', schema=None) as batch_op:
        batch_op.alter_column('budget_entry_id', new_column_name="budget_entry")
