"""initial migration

Revision ID: fecedb5b330a
Revises: 
Create Date: 2021-06-06 20:36:32.723661

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'fecedb5b330a'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
	op.create_table('account_history',
		sa.Column('id', sa.Integer(), autoincrement=False, nullable=False),
		sa.Column('created', sa.DateTime(), autoincrement=False, nullable=True),
		sa.Column('institution_id', sa.Integer(), autoincrement=False, nullable=True),
		sa.Column('name', sa.String(), autoincrement=False, nullable=True),
		sa.Column('version', sa.Integer(), autoincrement=False, nullable=False),
		sa.Column('changed', sa.DateTime(), nullable=True),
		sa.PrimaryKeyConstraint('id', 'version')
	)
	op.create_index(op.f('ix_account_history_id'), 'account_history', ['id'], unique=False)
	op.create_table('institution',
		sa.Column('id', sa.Integer(), nullable=False),
		sa.Column('name', sa.String(), nullable=True),
		sa.Column('aba_routing_number', sa.Integer(), nullable=True),
		sa.PrimaryKeyConstraint('id')
	)
	op.create_index(op.f('ix_institution_id'), 'institution', ['id'], unique=False)
	op.create_table('transaction',
		sa.Column('id', sa.Integer(), nullable=False),
		sa.Column('amount', sa.Float(), nullable=True),
		sa.PrimaryKeyConstraint('id')
	)
	op.create_index(op.f('ix_transaction_id'), 'transaction', ['id'], unique=False)
	op.create_table('user',
		sa.Column('id', sa.Integer(), nullable=False),
		sa.Column('email', sa.String(), nullable=True),
		sa.Column('username', sa.String(), nullable=True),
		sa.PrimaryKeyConstraint('id')
	)
	op.create_index(op.f('ix_user_id'), 'user', ['id'], unique=False)
	op.create_index(op.f('ix_user_username'), 'user', ['username'], unique=False)
	op.create_table('account',
		sa.Column('id', sa.Integer(), nullable=False),
		sa.Column('created', sa.DateTime(), nullable=True),
		sa.Column('institution_id', sa.Integer(), nullable=True),
		sa.Column('name', sa.String(), nullable=True),
		sa.Column('version', sa.Integer(), nullable=False),
		sa.ForeignKeyConstraint(['institution_id'], ['institution.id'], ),
		sa.PrimaryKeyConstraint('id'),
		sqlite_autoincrement=True
	)
	op.create_index(op.f('ix_account_id'), 'account', ['id'], unique=False)
	op.create_table('account_permission',
		sa.Column('id', sa.Integer(), nullable=False),
		sa.Column('account_id', sa.Integer(), nullable=True),
		sa.Column('type', sa.Enum('owner', name='accountpermissiontype'), nullable=True),
		sa.Column('user_id', sa.Integer(), nullable=True),
		sa.ForeignKeyConstraint(['account_id'], ['account.id'], ),
		sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
		sa.PrimaryKeyConstraint('id')
	)
	op.create_index(op.f('ix_account_permission_id'), 'account_permission', ['id'], unique=False)


def downgrade():
	pass
