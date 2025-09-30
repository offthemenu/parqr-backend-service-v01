"""Add chat messages table and user profile fields

Revision ID: 55b3e82ac554
Revises: 0027e4c1c22b
Create Date: 2025-08-11 16:27:04.701263

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '55b3e82ac554'
down_revision: Union[str, Sequence[str], None] = '0027e4c1c22b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add new user profile columns
    op.add_column('users', sa.Column('profile_deep_link', sa.String(length=255), nullable=True))
    op.add_column('users', sa.Column('profile_bio', sa.Text(), nullable=True))
    op.add_column('users', sa.Column('profile_display_name', sa.String(length=100), nullable=True))
    op.add_column('users', sa.Column('qr_image_path', sa.String(length=500), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    # Remove user profile columns
    op.drop_column('users', 'qr_image_path')
    op.drop_column('users', 'profile_display_name')
    op.drop_column('users', 'profile_bio')
    op.drop_column('users', 'profile_deep_link')
