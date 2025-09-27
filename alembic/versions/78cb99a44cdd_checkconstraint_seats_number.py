"""checkconstraint seats_number

Revision ID: 78cb99a44cdd
Revises: dd815ad91335
Create Date: 2025-09-27 10:35:58.492612

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '78cb99a44cdd'
down_revision = 'dd815ad91335'
branch_labels = None
depends_on = None


def upgrade():
    # Добавляем CHECK constraint через batch-операцию
    with op.batch_alter_table('tables') as batch_op:
        batch_op.create_check_constraint(
            'check_seats_positive',
            'seats_number > 0'
        )

def downgrade():
    with op.batch_alter_table('tables') as batch_op:
        batch_op.drop_constraint('check_seats_positive', type_='check')
