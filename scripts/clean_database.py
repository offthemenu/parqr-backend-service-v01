import sys
import os
from pathlib import Path

# Add parent directory to Python path
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.user import User
from app.models.car import Car
from app.models.parking_session import ParkingSession

def clean_database():
    """Clean all data from the database"""
    print("🗑️  Starting database cleanup...")
    
    db = SessionLocal()
    
    try:
        # Get current counts
        users_count = db.query(User).count()
        cars_count = db.query(Car).count()
        sessions_count = db.query(ParkingSession).count()
        
        print(f"📊 Current data:")
        print(f"   Users: {users_count}")
        print(f"   Cars: {cars_count}")
        print(f"   Parking Sessions: {sessions_count}")
        
        if users_count == 0 and cars_count == 0 and sessions_count == 0:
            print("✅ Database is already empty")
            return
        
        # Auto-confirm deletion for non-interactive environments
        print(f"\n⚠️  Proceeding with deletion of ALL {users_count + cars_count + sessions_count} records...")
        
        # Delete in correct order (respecting foreign key constraints)
        print("🗑️  Deleting parking sessions...")
        db.query(ParkingSession).delete()
        
        print("🗑️  Deleting cars...")
        db.query(Car).delete()
        
        print("🗑️  Deleting users...")
        db.query(User).delete()
        
        # Commit all deletions
        db.commit()
        
        # Verify cleanup
        final_users = db.query(User).count()
        final_cars = db.query(Car).count()
        final_sessions = db.query(ParkingSession).count()
        
        print(f"\n📊 After cleanup:")
        print(f"   Users: {final_users}")
        print(f"   Cars: {final_cars}")
        print(f"   Parking Sessions: {final_sessions}")
        
        if final_users == 0 and final_cars == 0 and final_sessions == 0:
            print("✅ Database cleaned successfully!")
        else:
            print("⚠️  Some records may still exist")
            
    except Exception as e:
        print(f"❌ Error cleaning database: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    clean_database()