"""dropping the machines table

Revision ID: 5741706f72f1
Revises: 
Create Date: 2023-06-27 20:52:58.797057

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5741706f72f1'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_table('machines')
    pass


def downgrade() -> None:
    pass
