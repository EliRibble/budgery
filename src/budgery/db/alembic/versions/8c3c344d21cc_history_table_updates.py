"""test

Revision ID: 8c3c344d21cc
Revises: 1b66153a9da4
Create Date: 2023-12-04 14:58:24.422743

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8c3c344d21cc'
down_revision = '1b66153a9da4'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('account_history', schema=None) as batch_op:
        batch_op.create_foreign_key(batch_op.f('fk_account_institution_id_institution'), 'institution', ['institution_id'], ['id'])

    with op.batch_alter_table('budget_entry_history', schema=None) as batch_op:
        batch_op.create_foreign_key(batch_op.f('fk_budget_entry_budget_id_budget'), 'budget', ['budget_id'], ['id'])


def downgrade():
    with op.batch_alter_table('budget_entry_history', schema=None) as batch_op:
        batch_op.drop_constraint(batch_op.f('fk_budget_entry_budget_id_budget'), type_='foreignkey')

    with op.batch_alter_table('account_history', schema=None) as batch_op:
        batch_op.drop_constraint(batch_op.f('fk_account_institution_id_institution'), type_='foreignkey')

