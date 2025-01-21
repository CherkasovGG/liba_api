"""added to user bd counter of books

Revision ID: b1d7ba25a633
Revises: 3328d770b473
Create Date: 2025-01-21 01:15:25.504748

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "b1d7ba25a633"
down_revision: Union[str, None] = "3328d770b473"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column("users", sa.Column("books_count", sa.Integer(), nullable=False))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("users", "books_count")
    # ### end Alembic commands ###
