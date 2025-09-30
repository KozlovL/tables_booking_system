"""fix dish model

Revision ID: 3b1c5c2efbc0
Revises: 235c007243b5
Create Date: 2025-09-28 21:11:17.252846

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3b1c5c2efbc0'
down_revision = '235c007243b5'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('dish', schema=None) as batch_op:
        # Добавляем колонку cafe_id
        batch_op.add_column(sa.Column('cafe_id', sa.Integer(), nullable=False))
        # Создаем FK с именем
        batch_op.create_foreign_key(
            'fk_dish_cafe_id',  # имя constraint
            'cafe',             # целевая таблица
            ['cafe_id'],        # локальная колонка
            ['id']              # колонка в целевой таблице
        )
        # Удаляем старую колонку cafe
        batch_op.drop_column('cafe')


def downgrade():
    with op.batch_alter_table('dish', schema=None) as batch_op:
        # Добавляем обратно колонку cafe
        batch_op.add_column(sa.Column('cafe', sa.INTEGER(), nullable=False))
        # Удаляем FK с именем
        batch_op.drop_constraint('fk_dish_cafe_id', type_='foreignkey')
        # Если нужно, создаем FK для старой колонки cafe с именем
        batch_op.create_foreign_key(
            'fk_dish_cafe',  # имя constraint
            'cafe',
            ['cafe'],
            ['id']
        )
        # Удаляем колонку cafe_id
        batch_op.drop_column('cafe_id')
