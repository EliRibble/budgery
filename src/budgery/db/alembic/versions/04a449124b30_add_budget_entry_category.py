"""add budget entry category

Revision ID: 04a449124b30
Revises: b7158976a072
Create Date: 2021-07-10 21:32:58.648235

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '04a449124b30'
down_revision = 'b7158976a072'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('budget_entry', sa.Column('category', sa.String(), nullable=True))


def downgrade():
    op.drop_column('budget_entry', 'category')
