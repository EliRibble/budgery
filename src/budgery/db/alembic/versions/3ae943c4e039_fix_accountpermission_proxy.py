"""fix accountpermission proxy

Revision ID: 3ae943c4e039
Revises: 971adcf9d976
Create Date: 2021-06-15 09:37:39.281307

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3ae943c4e039'
down_revision = '971adcf9d976'
branch_labels = None
depends_on = None


def upgrade():
	with op.batch_alter_table("account_permission") as batch_op:
		batch_op.alter_column('account_id',
			existing_type=sa.INTEGER(),
			nullable=False)
		batch_op.alter_column('user_id',
			existing_type=sa.INTEGER(),
			nullable=False)
		batch_op.drop_index('ix_account_permission_id')
		batch_op.drop_column('id')


def downgrade():
	op.add_column('account_permission', sa.Column('id', sa.INTEGER(), nullable=False))
	op.create_index('ix_account_permission_id', 'account_permission', ['id'], unique=False)
	op.alter_column('account_permission', 'user_id',
		existing_type=sa.INTEGER(),
		nullable=True)
	op.alter_column('account_permission', 'account_id',
		existing_type=sa.INTEGER(),
		nullable=True)
