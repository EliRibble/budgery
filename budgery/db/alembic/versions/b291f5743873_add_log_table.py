"""add log table

Revision ID: b291f5743873
Revises: fecedb5b330a
Create Date: 2021-06-07 05:27:20.228708

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b291f5743873'
down_revision = 'fecedb5b330a'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('logentry',
		sa.Column('id', sa.Integer(), nullable=False),
		sa.Column('at', sa.DateTime(), nullable=True),
		sa.Column('content', sa.String(), nullable=True),
		sa.Column('user_id', sa.Integer(), nullable=True),
		sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
		sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_logentry_id'), 'logentry', ['id'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_logentry_id'), table_name='logentry')
    op.drop_table('logentry')
