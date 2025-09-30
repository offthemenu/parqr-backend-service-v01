"""optimize database indexes - remove redundancies and add performance indexes

Revision ID: 0027e4c1c22b
Revises: f5a103f780cb
Create Date: 2025-08-04 16:16:40.868588

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0027e4c1c22b'
down_revision: Union[str, Sequence[str], None] = 'f5a103f780cb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Remove redundant indexes that duplicate primary keys and unique constraints
    
    # Users table - remove redundant indexes
    op.drop_index('ix_users_id', table_name='users')
    op.drop_index('idx_users_qr_code_id', table_name='users')
    
    # Cars table - remove redundant index
    op.drop_index('ix_cars_id', table_name='cars')
    
    # Parking sessions table - remove redundant index
    op.drop_index('ix_parking_sessions_id', table_name='parking_sessions')
    
    # Add missing performance indexes
    
    # Index on signup_country_iso for country-based queries
    op.create_index('idx_users_signup_country_iso', 'users', ['signup_country_iso'])
    
    # Composite index for user's parking session history queries (user_id, start_time DESC)
    op.create_index('idx_parking_sessions_user_history', 'parking_sessions', ['user_id', 'start_time'])


def downgrade() -> None:
    """Downgrade schema."""
    # Remove the performance indexes we added
    op.drop_index('idx_users_signup_country_iso', table_name='users')
    op.drop_index('idx_parking_sessions_user_history', table_name='parking_sessions')
    
    # Restore the redundant indexes (for compatibility)
    op.create_index('ix_users_id', 'users', ['id'])
    op.create_index('idx_users_qr_code_id', 'users', ['qr_code_id'])
    op.create_index('ix_cars_id', 'cars', ['id'])
    op.create_index('ix_parking_sessions_id', 'parking_sessions', ['id'])
