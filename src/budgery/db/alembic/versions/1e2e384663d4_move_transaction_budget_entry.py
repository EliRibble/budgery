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
    with op.batch_alter_table('budget_entry_history', schema=None) as batch_op:
        batch_op.create_foreign_key(None, 'budget', ['budget_id'], ['id'])

    with op.batch_alter_table('transaction', schema=None) as batch_op:
        batch_op.add_column(sa.Column('budget_entry_id', sa.Integer(), nullable=True))
        batch_op.drop_constraint('fk_budget_entry_id', type_='foreignkey')
        batch_op.create_foreign_key('fk_budget_entry_id', 'budget_entry', ['budget_entry_id'], ['id'])
        batch_op.drop_column('budget_entry')


def downgrade():
    with op.batch_alter_table('transaction', schema=None) as batch_op:
        batch_op.add_column(sa.Column('budget_entry', sa.INTEGER(), nullable=True))
        batch_op.drop_constraint('fk_budget_entry_id', type_='foreignkey')
        batch_op.create_foreign_key('fk_budget_entry_id', 'budget_entry', ['budget_entry'], ['id'])
        batch_op.drop_column('budget_entry_id')

    with op.batch_alter_table('budget_entry_history', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
