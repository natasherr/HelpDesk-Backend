"""Change

Revision ID: ed3b3d48bdec
Revises: f35b2fee0d91
Create Date: 2025-02-25 13:01:14.649040

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ed3b3d48bdec'
down_revision = 'f35b2fee0d91'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_column('created_at')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('created_at', sa.DATETIME(), nullable=True))

    # ### end Alembic commands ###
