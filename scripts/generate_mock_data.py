import sys
import os
from pathlib import Path

# Add parent directory to Python path
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

from datetime import datetime, timedelta, timezone
import random
import secrets
import string
import hashlib
import uuid
from sqlalchemy.orm import Session
from app.db.session import SessionLocal, engine
from app.models.user import User
from app.models.car import Car
from app.models.parking_session import ParkingSession
from .country_codes import SERVICING_COUNTRIES

def generate_user_code() -> str:
    """Generate 8-character alphanumeric user code (matching user.py logic)"""
    return ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(8))

def generate_qr_code_id(user_code: str, phone_number: str) -> str:
    """Generate unique QR code ID (matching user.py logic)"""
    unique_string = f"{user_code}_{phone_number}_{uuid.uuid4().hex[:8]}"
    hash_object = hashlib.sha256(unique_string.encode())
    short_hash = hash_object.hexdigest()[:8].upper()
    return f"QR_{short_hash}"

def generate_phone_number_by_country(country_iso: str) -> str:
    """Generate realistic phone number based on country"""
    if country_iso == "KR":
        # Korean mobile format: 01012345678
        return f"010{random.randint(10000000, 99999999)}"
    elif country_iso == "US" or country_iso == "CA":
        # US/Canada format: +1XXXXXXXXXX
        return f"+1{random.randint(2000000000, 9999999999)}"
    elif country_iso == "JP":
        # Japan mobile format: +8190XXXXXXXX
        return f"+8190{random.randint(10000000, 99999999)}"
    elif country_iso == "CN":
        # China mobile format: +861XXXXXXXXXX
        return f"+861{random.randint(300000000, 999999999)}"
    elif country_iso == "GB":
        # UK mobile format: +447XXXXXXXXX
        return f"+447{random.randint(100000000, 999999999)}"
    elif country_iso == "DE":
        # Germany mobile format: +4915XXXXXXXXX
        return f"+4915{random.randint(100000000, 999999999)}"
    elif country_iso == "FR":
        # France mobile format: +336XXXXXXXX
        return f"+336{random.randint(10000000, 99999999)}"
    elif country_iso == "AU":
        # Australia mobile format: +614XXXXXXXX
        return f"+614{random.randint(10000000, 99999999)}"
    else:
        # Generic international format for other countries
        country_info = None
        for name, info in SERVICING_COUNTRIES.items():
            if info["country_iso"] == country_iso:
                country_info = info
                break
        
        if country_info:
            country_code = country_info["country_code"]
            # Generate 8-10 digit number after country code
            digits = random.randint(10000000, 9999999999)
            return f"{country_code}{digits}"
        else:
            # Fallback
            return f"+{random.randint(1, 999)}{random.randint(100000000, 9999999999)}"

def generate_license_plate() -> str:
    """Generate realistic Korean license plate"""
    # Common Korean characters used in license plates
    korean_chars = ['가', '나', '다', '라', '마', '차', '카', '타', '파','하', '거', '너', '더', '러', '머', '버', '서', '어', '저', '처', '커', '터', '퍼', '허','고', '노', '도','로', '모', '보', '소', '오', '조', '초', '코', '토', '포', '호']
    # Korean license plate format: 12가3456 or 가12나3456
    # Using simplified format: 가1234 (1 Korean char + 4 numbers)
    korean_char = random.choice(korean_chars)
    numbers_prefix = ''.join(random.choices(string.digits, k=3))
    numbers_suffix = ''.join(random.choices(string.digits, k=4))
    return f"{numbers_prefix}{korean_char}{numbers_suffix}"

def create_mock_users(db: Session, count: int = 10) -> list[User]:
    """Create mock users with diverse country representation"""
    users = []
    used_phones = set()
    
    # Get list of available countries
    available_countries = list(SERVICING_COUNTRIES.values())
    
    for _ in range(count):
        user_code = generate_user_code()
        # Ensure unique user_code
        while db.query(User).filter(User.user_code == user_code).first():
            user_code = generate_user_code()
        
        # Randomly select a country (with bias towards South Korea for demo)
        if random.random() <  1:  # 60% chance of South Korea
            country_info = {"country_iso": "KR", "country_code": "+82"}
        else:
            country_info = random.choice(available_countries)
        
        country_iso = country_info["country_iso"]
        
        # Generate country-appropriate phone number
        phone_number = generate_phone_number_by_country(country_iso)
        
        # For Korean numbers, ensure they follow the registration logic
        if country_iso == "KR":
            # Convert to international format like the registration endpoint does
            if phone_number.startswith("010"):
                phone_number_clean = f"+82{phone_number[1:]}"
            else:
                phone_number_clean = phone_number
        else:
            phone_number_clean = phone_number
        
        # Ensure uniqueness
        while (phone_number_clean in used_phones or 
               db.query(User).filter(User.phone_number == phone_number_clean).first()):
            phone_number = generate_phone_number_by_country(country_iso)
            if country_iso == "KR" and phone_number.startswith("010"):
                phone_number_clean = f"+82{phone_number[1:]}"
            else:
                phone_number_clean = phone_number
        used_phones.add(phone_number_clean)
        
        # Generate QR code using proper logic
        qr_code_id = generate_qr_code_id(user_code, phone_number_clean)
        
        user = User(
            phone_number=phone_number_clean,
            user_code=user_code,
            qr_code_id=qr_code_id,
            signup_country_iso=country_iso
        )
        db.add(user)
        users.append(user)
    
    db.commit()
    print(f"✅ Created {count} mock users")
    return users

def create_mock_cars(db: Session, users: list[User], cars_per_user: int = 1) -> list[Car]:
    """Create mock cars for users"""
    car_brands = ["Toyota", "Honda", "Ford", "BMW", "Mercedes Benz", "Audi", "Hyundai"]
    car_models = {
        "Toyota": ["Camry", "Corolla", "Prius", "RAV4"],
        "Honda": ["Civic", "Accord", "CR-V", "Pilot"],
        "Ford": ["F-150", "Explorer", "Escape", "Mustang"],
        "BMW": ["320i", "X3", "X5", "520d"],
        "Mercedes Benz": ["C220d", "E300", "GLC350", "S550"],
        "Audi": ["A4", "Q5", "A6", "Q7"],
        "Hyundai": ["Elantra", "Sonata", "Tucson", "Santa Fe"]
    }
    
    cars = []
    
    for user in users:
        num_cars = random.randint(1, cars_per_user)
        for _ in range(num_cars):
            brand = random.choice(car_brands)
            model = random.choice(car_models[brand])
            license_plate = generate_license_plate()
            
            # Ensure unique license plate
            while db.query(Car).filter(Car.license_plate == license_plate).first():
                license_plate = generate_license_plate()
            
            car = Car(
                owner_id=user.id,
                license_plate=license_plate,
                car_brand=brand,
                car_model=model
            )
            db.add(car)
            cars.append(car)
    
    db.commit()
    print(f"✅ Created {len(cars)} mock cars")
    return cars

def create_mock_parking_sessions(db: Session, users: list[User], cars: list[Car], sessions_count: int = 50):
    """Create mock parking sessions"""
    # Optional parking note examples (realistic user inputs)
    parking_notes = [
        "Section G8",
        "Level B3", 
        "Near elevator",
        "Spot 47",
        "Level 2, Zone A",
        "Close to entrance",
        "Section C, Row 5",
        "Parking Structure 3",
        "Ground floor",
        "Level P1, near exit",
        "Visitor parking",
        "Row D, spot 23",
        "Near mall entrance",
        "Level -1, Section B"
    ]
    
    # Create coordinate ranges for Seoul metropolitan area
    lat_range = (37.4, 37.7)  # Seoul latitude bounds
    lng_range = (126.8, 127.2)  # Seoul longitude bounds
    
    for _ in range(sessions_count):
        user = random.choice(users)
        # Get user's cars
        user_cars = [car for car in cars if car.owner_id == user.id]
        if not user_cars:
            continue
            
        car = random.choice(user_cars)
        
        # Generate random start time in the past 30 days (with UTC timezone)
        start_time = datetime.now(timezone.utc) - timedelta(
            days=random.randint(0, 30),
            hours=random.randint(0, 23),
            minutes=random.randint(0, 59)
        )
        
        # 70% chance session is ended
        end_time = None
        if random.random() < 0.7:
            end_time = start_time + timedelta(
                hours=random.randint(1, 8),
                minutes=random.randint(0, 59)
            )
        
        # 40% chance of having a parking note (mimics real usage)
        note_location = None
        if random.random() < 0.4:
            note_location = random.choice(parking_notes)
        
        session = ParkingSession(
            user_id=user.id,
            car_id=car.id,
            start_time=start_time,
            end_time=end_time,
            note_location=note_location,
            latitude=random.uniform(*lat_range),
            longitude=random.uniform(*lng_range)
        )
        db.add(session)
    
    db.commit()
    print(f"✅ Created {sessions_count} mock parking sessions")

def main():
    """Generate all mock data"""
    print("🚀 Starting mock data generation...")
    
    # Create database session
    db = SessionLocal()
    
    try:
        # Check if data already exists
        user_count = db.query(User).count()
        if user_count > 0:
            print(f"Database has {user_count} users. Proceeding to add more data...")
        
        # Generate data
        users = create_mock_users(db, count=10)
        cars = create_mock_cars(db, users, cars_per_user=1)
        create_mock_parking_sessions(db, users, cars, sessions_count=30)
        
        # Print summary
        total_users = db.query(User).count()
        total_cars = db.query(Car).count()
        total_sessions = db.query(ParkingSession).count()
        active_sessions = db.query(ParkingSession).filter(ParkingSession.end_time.is_(None)).count()
        
        # Country distribution  
        from sqlalchemy import func
        country_stats = db.query(User.signup_country_iso, 
                                func.count(User.id).label('count'))\
                         .group_by(User.signup_country_iso)\
                         .all()
        
        print("\n📊 Database Summary:")
        print(f"   Users: {total_users}")
        print(f"   Cars: {total_cars}")
        print(f"   Total Sessions: {total_sessions}")
        print(f"   Active Sessions: {active_sessions}")
        print(f"   Completed Sessions: {total_sessions - active_sessions}")
        
        print("\n🌍 Country Distribution:")
        for country_iso, count in country_stats:
            # Find country name
            country_name = "Unknown"
            for name, info in SERVICING_COUNTRIES.items():
                if info["country_iso"] == country_iso:
                    country_name = name
                    break
            print(f"   {country_name} ({country_iso}): {count} users")
        
        print("\n✅ Mock data generation completed!")
        
    except Exception as e:
        print(f"❌ Error generating mock data: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    main()