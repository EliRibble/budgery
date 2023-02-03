"""transaction use sourcink

Revision ID: 462cce0b5c7e
Revises: 3ae943c4e039
Create Date: 2021-06-15 15:19:10.306628

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '462cce0b5c7e'
down_revision = '3ae943c4e039'
branch_labels = None
depends_on = None


def upgrade():
	op.add_column('sourcink', sa.Column('account_id', sa.Integer(), nullable=True))
	with op.batch_alter_table("sourcink") as batch_op:
		batch_op.create_foreign_key('fk_account_id', 'sourcink', ['account_id'], ['id'])
	with op.batch_alter_table("transaction") as batch_op:
		batch_op.drop_constraint('fk_account_id_from', type_='foreignkey')
		batch_op.drop_constraint('fk_account_id_to', type_='foreignkey')
		batch_op.drop_column('account_id_from')
		batch_op.drop_column('account_id_to')


def downgrade():
	op.add_column('transaction', sa.Column('account_id_to', sa.INTEGER(), nullable=True))
	op.add_column('transaction', sa.Column('account_id_from', sa.INTEGER(), nullable=True))
	op.create_foreign_key('fk_account_id_to', 'transaction', 'account', ['account_id_to'], ['id'])
	op.create_foreign_key('fk_account_id_from', 'transaction', 'account', ['account_id_from'], ['id'])
	op.drop_constraint('fk_account_id', 'sourcink', type_='foreignkey')
	op.drop_column('sourcink', 'account_id')
