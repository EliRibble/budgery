"""add import job

Revision ID: bf2c79c82fb0
Revises: 462cce0b5c7e
Create Date: 2021-06-16 15:28:41.280155

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'bf2c79c82fb0'
down_revision = '462cce0b5c7e'
branch_labels = None
depends_on = None


def upgrade():
	op.create_table('import_job',
		sa.Column('id', sa.Integer(), nullable=False),
		sa.Column('created', sa.DateTime(), nullable=True),
		sa.Column('filename', sa.String(), nullable=True),
		sa.Column('status', sa.Enum('error', 'started', 'finished', name='importjobstatus'), nullable=True),
		sa.Column('user_id', sa.Integer(), nullable=False),
		sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
		sa.PrimaryKeyConstraint('id')
	)
	op.create_index(op.f('ix_import_job_id'), 'import_job', ['id'], unique=False)

	with op.batch_alter_table("sourcink") as batch_op:
		batch_op.drop_constraint('fk_account_id', type_='foreignkey')
		batch_op.create_foreign_key('fk_account_id', 'account', ['account_id'], ['id'])

	with op.batch_alter_table("transaction") as batch_op:
		batch_op.add_column(sa.Column('import_job_id', sa.Integer(), nullable=True))
		batch_op.create_foreign_key('fk_import_job_id', 'import_job', ['import_job_id'], ['id'])


def downgrade():
    op.drop_constraint('fk_import_job_id', 'transaction', type_='foreignkey')
    op.drop_column('transaction', 'import_job_id')
    op.drop_constraint('fk_account_id', 'sourcink', type_='foreignkey')
    op.create_foreign_key('fk_account_id', 'sourcink', 'sourcink', ['account_id'], ['id'])
    op.drop_index(op.f('ix_import_job_id'), table_name='import_job')
    op.drop_table('import_job')
