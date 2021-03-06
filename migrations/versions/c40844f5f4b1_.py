"""empty message

Revision ID: c40844f5f4b1
Revises: 77c4a4a265a9
Create Date: 2020-03-08 14:30:56.954335

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c40844f5f4b1'
down_revision = '77c4a4a265a9'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Venue', sa.Column('seeking_description', sa.String(length=2500), nullable=True))
    op.drop_column('Venue', 'seeking_descrption')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Venue', sa.Column('seeking_descrption', sa.VARCHAR(length=2500), autoincrement=False, nullable=True))
    op.drop_column('Venue', 'seeking_description')
    # ### end Alembic commands ###
