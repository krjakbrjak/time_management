"""Created user

Revision ID: d1d41a33522e
Revises:
Create Date: 2020-10-16 16:31:42.356854

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "d1d41a33522e"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "user",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("username", sa.String(length=250), nullable=False),
        sa.Column("full_name", sa.String(length=250), nullable=True),
        sa.Column("email", sa.String(), nullable=True),
        sa.Column("disabled", sa.Boolean(), nullable=False),
        sa.Column("hashed_password", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("username"),
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("user")
    # ### end Alembic commands ###