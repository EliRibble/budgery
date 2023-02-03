"""remove budget type

Revision ID: b7158976a072
Revises: 45c9f6797fea
Create Date: 2021-06-23 22:26:51.943874

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b7158976a072'
down_revision = '45c9f6797fea'
branch_labels = None
depends_on = None


def upgrade():
	with op.batch_alter_table("budget") as batch_op:
		batch_op.drop_column('type')
	with op.batch_alter_table("budget_history") as batch_op:
		batch_op.drop_column('type')


def downgrade():
	op.add_column('budget_history', sa.Column('type', sa.VARCHAR(length=5), nullable=True))
	op.add_column('budget', sa.Column('type', sa.VARCHAR(length=5), nullable=True))
