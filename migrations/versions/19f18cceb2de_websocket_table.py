"""websocket table

Revision ID: 19f18cceb2de
Revises: 
Create Date: 2023-05-07 18:31:41.663564

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "19f18cceb2de"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "websocket_connections",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("wsock", sa.JSON(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id"),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("websocket_connections")
    # ### end Alembic commands ###
