"""add import_job.account_id

Revision ID: 566d8d8847e4
Revises: 04a449124b30
Create Date: 2022-04-21 16:53:26.067429

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '566d8d8847e4'
down_revision = '04a449124b30'
branch_labels = None
depends_on = None


def upgrade():
	op.add_column('import_job', sa.Column('account_id', sa.Integer(), nullable=True))
	with op.batch_alter_table("import_job") as batch_op:
   		batch_op.create_foreign_key("fk_import_job_account_id", 'account', ['account_id'], ['id'])


def downgrade():
   	op.drop_constraint(None, 'import_job', type_='foreignkey')
   	op.drop_column('import_job', 'account_id')
