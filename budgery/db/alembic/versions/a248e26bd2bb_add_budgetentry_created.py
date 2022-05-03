"""add budgetentry.created

Revision ID: a248e26bd2bb
Revises: 59a9c3445a9b
Create Date: 2022-05-03 11:51:33.351141

"""
import datetime
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a248e26bd2bb'
down_revision = '59a9c3445a9b'
branch_labels = None
depends_on = None


def upgrade():
	op.add_column('budget_entry', sa.Column('created', sa.DateTime(), nullable=True))
	op.add_column('budget_entry_history', sa.Column('created', sa.DateTime(), autoincrement=False, nullable=True, server_default=datetime.datetime(
		year=2000,
		month=1,
		day=1,
		hour=0,
		minute=0,
		second=0,
	).isoformat()))


def downgrade():
	op.drop_column('budget_entry_history', 'created')
	op.drop_column('budget_entry', 'created')
