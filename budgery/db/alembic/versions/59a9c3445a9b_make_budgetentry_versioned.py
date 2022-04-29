"""make budgetentry versioned

Revision ID: 59a9c3445a9b
Revises: 39306bfc0cf3
Create Date: 2022-04-29 08:50:46.096572

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '59a9c3445a9b'
down_revision = '39306bfc0cf3'
branch_labels = None
depends_on = None


def upgrade():
	op.create_table('budget_entry_history',
		sa.Column('id', sa.Integer(), autoincrement=False, nullable=False),
		sa.Column('budget_id', sa.Integer(), autoincrement=False, nullable=True),
		sa.Column('amount', sa.Float(), autoincrement=False, nullable=True),
		sa.Column('category', sa.String(), autoincrement=False, nullable=True),
		sa.Column('name', sa.String(), autoincrement=False, nullable=True),
		sa.Column('version', sa.Integer(), autoincrement=False, nullable=False),
		sa.Column('changed', sa.DateTime(), nullable=True),
		sa.PrimaryKeyConstraint('id', 'version')
    )
	op.create_index(op.f('ix_budget_entry_history_id'), 'budget_entry_history', ['id'], unique=False)
	op.add_column('budget_entry', sa.Column('version', sa.Integer(), nullable=False, server_default="1"))


def downgrade():
	op.drop_column('budget_entry', 'version')
	op.drop_index(op.f('ix_budget_entry_history_id'), table_name='budget_entry_history')
	op.drop_table('budget_entry_history')
