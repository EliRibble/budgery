"""add transaction fks

Revision ID: 971adcf9d976
Revises: b291f5743873
Create Date: 2021-06-07 09:49:03.708797

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '971adcf9d976'
down_revision = 'b291f5743873'
branch_labels = None
depends_on = None


def upgrade():
	op.create_table('sourcink',
		sa.Column('id', sa.Integer(), nullable=False),
		sa.Column('name', sa.String(), nullable=True),
		sa.PrimaryKeyConstraint('id')
	)
	op.create_index(op.f('ix_sourcink_id'), 'sourcink', ['id'], unique=False)
	op.add_column('transaction', sa.Column('account_id_from', sa.Integer(), nullable=True))
	op.add_column('transaction', sa.Column('account_id_to', sa.Integer(), nullable=True))
	op.add_column('transaction', sa.Column('at', sa.DateTime(), nullable=True))
	op.add_column('transaction', sa.Column('category', sa.String(), nullable=True))
	op.add_column('transaction', sa.Column('sourcink_id_from', sa.Integer(), nullable=True))
	op.add_column('transaction', sa.Column('sourcink_id_to', sa.Integer(), nullable=True))
	with op.batch_alter_table("transaction") as batch_op:
		batch_op.create_foreign_key("fk_account_id_from", 'account', ['account_id_from'], ['id'])
		batch_op.create_foreign_key("fk_account_id_to", 'account', ['account_id_to'], ['id'])
		batch_op.create_foreign_key("fk_sourcink_id_from", 'sourcink', ['sourcink_id_from'], ['id'])
		batch_op.create_foreign_key("fk_sourcink_id_to", 'sourcink', ['sourcink_id_to'], ['id'])


def downgrade():
	op.drop_constraint(None, 'transaction', type_='foreignkey')
	op.drop_constraint(None, 'transaction', type_='foreignkey')
	op.drop_constraint(None, 'transaction', type_='foreignkey')
	op.drop_constraint(None, 'transaction', type_='foreignkey')
	op.drop_column('transaction', 'sourcink_id_to')
	op.drop_column('transaction', 'sourcink_id_from')
	op.drop_column('transaction', 'category')
	op.drop_column('transaction', 'at')
	op.drop_column('transaction', 'account_id_to')
	op.drop_column('transaction', 'account_id_from')
	op.drop_index(op.f('ix_sourcink_id'), table_name='sourcink')
	op.drop_table('sourcink')
