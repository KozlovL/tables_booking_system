"""merge migration branches

Revision ID: 4c9032aaa4de
Revises: 75c659b823c2, 7be8e5fae96b
Create Date: 2025-09-26 13:27:11.019139

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4c9032aaa4de'
down_revision = ('75c659b823c2', '7be8e5fae96b')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
