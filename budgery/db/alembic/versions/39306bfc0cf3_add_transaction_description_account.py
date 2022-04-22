"""add transaction description, account

Revision ID: 39306bfc0cf3
Revises: 566d8d8847e4
Create Date: 2022-04-21 17:43:07.045872

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '39306bfc0cf3'
down_revision = '566d8d8847e4'
branch_labels = None
depends_on = None


def upgrade():
	op.add_column('transaction', sa.Column('account_id_from', sa.Integer(), nullable=True))
	op.add_column('transaction', sa.Column('account_id_to', sa.Integer(), nullable=True))
	op.add_column('transaction', sa.Column('description', sa.String(), nullable=True))
	with op.batch_alter_table("transaction") as batch_op:
		batch_op.create_foreign_key('fk_account_id_to', 'account', ['account_id_to'], ['id'])
		batch_op.create_foreign_key('fk_account_id_from', 'account', ['account_id_from'], ['id'])


def downgrade():
	op.drop_constraint('fk_account_id_from', 'transaction', type_='foreignkey')
	op.drop_constraint('fk_account_id_to', 'transaction', type_='foreignkey')
	op.drop_column('transaction', 'description')
	op.drop_column('transaction', 'account_id_to')
	op.drop_column('transaction', 'account_id_from')
	op.alter_column('import_job', 'user_id',
		existing_type=sa.INTEGER(),
		nullable=False)
