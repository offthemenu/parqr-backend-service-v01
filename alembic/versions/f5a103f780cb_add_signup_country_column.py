"""Add signup country column

Revision ID: f5a103f780cb
Revises: a70973a3fcd8
Create Date: 2025-08-04 11:23:06.033263

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f5a103f780cb'
down_revision: Union[str, Sequence[str], None] = 'a70973a3fcd8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add signup_country_iso column to users table
    op.add_column('users', sa.Column('signup_country_iso', sa.String(length=5), nullable=False, server_default='KR'))
    
    # Remove server default after column is added
    op.alter_column('users', 'signup_country_iso', server_default=None)


def downgrade() -> None:
    """Downgrade schema."""
    # Remove signup_country_iso column from users table
    op.drop_column('users', 'signup_country_iso')
