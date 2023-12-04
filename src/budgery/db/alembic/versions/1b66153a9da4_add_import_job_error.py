"""add import_job.error

Revision ID: 1b66153a9da4
Revises: 98cb7dbad3cb
Create Date: 2023-12-04 14:30:04.270805

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1b66153a9da4'
down_revision = '98cb7dbad3cb'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('import_job', schema=None) as batch_op:
        batch_op.add_column(sa.Column('error', sa.Enum('NONE', 'FAILED_PARSING_FILE', name='importjoberror'), nullable=True))
        batch_op.alter_column('user_id',
               existing_type=sa.INTEGER(),
               nullable=True)


def downgrade():
    with op.batch_alter_table('import_job', schema=None) as batch_op:
        batch_op.alter_column('user_id',
               existing_type=sa.INTEGER(),
               nullable=False)
        batch_op.drop_column('error')
