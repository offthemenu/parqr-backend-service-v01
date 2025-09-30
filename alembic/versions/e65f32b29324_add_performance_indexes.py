"""Add performance indexes

Revision ID: e65f32b29324
Revises: 86041de9befc
Create Date: 2025-07-30 17:04:07.218131

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = 'e65f32b29324'
down_revision = '86041de9befc'
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Add index on users.qr_code_id for QR code lookups
    op.create_index('idx_users_qr_code_id', 'users', ['qr_code_id'])
    
    # Add index on cars.owner_id for user car queries (/my-cars endpoint)
    op.create_index('idx_cars_owner_id', 'cars', ['owner_id'])
    
    # Add index on parking_sessions.user_id for user session queries
    op.create_index('idx_parking_sessions_user_id', 'parking_sessions', ['user_id'])
    
    # Add index on parking_sessions.car_id for car session queries
    op.create_index('idx_parking_sessions_car_id', 'parking_sessions', ['car_id'])
    
    # Add index on parking_sessions.start_time for time-based queries
    op.create_index('idx_parking_sessions_start_time', 'parking_sessions', ['start_time'])
    
    # Add index on parking_sessions.end_time for session completion queries
    op.create_index('idx_parking_sessions_end_time', 'parking_sessions', ['end_time'])

def downgrade() -> None:
    op.drop_index('idx_parking_sessions_end_time', table_name='parking_sessions')
    op.drop_index('idx_parking_sessions_start_time', table_name='parking_sessions')
    op.drop_index('idx_parking_sessions_car_id', table_name='parking_sessions')
    op.drop_index('idx_parking_sessions_user_id', table_name='parking_sessions')
    op.drop_index('idx_cars_owner_id', table_name='cars')
    op.drop_index('idx_users_qr_code_id', table_name='users')