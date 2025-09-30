# parQR Mock Data Generation Guide

This guide explains how the `generate_mock_data.py` script creates realistic test data for your parQR application development and testing.

## Overview

The mock data generator creates a complete dataset that mirrors real-world usage patterns, including users, cars, and parking sessions with proper relationships and realistic data distribution.

## Script Architecture

### File Location
```
parqr-backend/scripts/generate_mock_data.py
```

### Dependencies
- **Database Models**: User, Car, ParkingSession
- **Authentication Logic**: Matches user registration patterns
- **Timezone Handling**: Uses UTC timestamps like production
- **Unique Constraints**: Respects all database uniqueness requirements

## Korean Localization Features

The mock data generator is specifically designed for the Korean market with authentic local data patterns:

### **Phone Numbers**
- **Format**: Korean mobile format `+82XXXXXXXXXX`
- **Range**: 10-digit numbers starting with country code +82
- **Example**: `+821012345678`, `+821098765432`

### **License Plates**
- **Format**: Korean standard `123가4567` (3 digits + Hangul + 4 digits)
- **Characters**: 42 authentic Hangul characters used in Korean license plates
- **Examples**: `123가4567`, `456나8901`, `789서2345`

**Supported Hangul Characters:**
```
가, 나, 다, 라, 마, 차, 카, 타, 파, 하
거, 너, 더, 러, 머, 버, 서, 어, 저, 처, 커, 터, 퍼, 허  
고, 노, 도, 로, 모, 보, 소, 오, 조, 초, 코, 토, 포, 호
```

### **Geographic Coordinates**
- **Location**: Seoul metropolitan area
- **Latitude Range**: 37.4-37.7 (Seoul city bounds)
- **Longitude Range**: 126.8-127.2 (Seoul city bounds)

## Data Generation Strategy

### 1. User Generation (`create_mock_users()`)

**Generates:** 15 users by default

**Key Features:**
- **Phone Numbers**: Korean format `+82XXXXXXXXXX` (10-digit mobile numbers)
- **User Codes**: 8-character alphanumeric codes (matching production logic)
- **QR Code IDs**: SHA-256 generated using same algorithm as `user.py`
- **Uniqueness**: Prevents duplicate phone numbers and user codes

**Example Generated User:**
```python
User(
    phone_number="+821012345678",
    user_code="AB7X9K2M",
    qr_code_id="QR_A1B2C3D4",
    created_at="2024-07-30T10:30:00Z"
)
```

### 2. Car Generation (`create_mock_cars()`)

**Generates:** 1-3 cars per user

**Key Features:**
- **Realistic Brands**: Toyota, Honda, Ford, BMW, Mercedes, Audi, Hyundai, Nissan
- **Brand-Matched Models**: Each brand has appropriate model list
- **License Plates**: Korean format `123가4567` with Hangul characters
- **Owner Relationships**: Properly linked to user IDs

**Example Generated Car:**
```python
Car(
    owner_id=1,
    license_plate="123가4567",
    car_brand="Toyota",
    car_model="Camry",
    created_at="2024-07-30T10:31:00Z"
)
```

**Brand-Model Mapping:**
```python
{
    "Toyota": ["Camry", "Corolla", "Prius", "RAV4"],
    "Honda": ["Civic", "Accord", "CR-V", "Pilot"],
    "BMW": ["3 Series", "X3", "X5", "5 Series"],
    # ... etc
}
```

### 3. Parking Session Generation (`create_mock_parking_sessions()`)

**Generates:** 75 parking sessions by default

**Key Features:**
- **Time Distribution**: Sessions spread across past 30 days
- **Session States**: 70% completed, 30% active (no end_time)
- **Duration Variety**: 1-8 hours for completed sessions
- **Geographic Data**: Seoul-like coordinates
- **User-Car Relationships**: Only creates sessions for user's own cars

**Example Generated Session:**
```python
ParkingSession(
    user_id=1,
    car_id=3,
    start_time="2024-07-25T14:30:00Z",
    end_time="2024-07-25T18:45:00Z",  # 70% chance of completion
    location="Downtown Parking Garage",
    latitude=37.7849,
    longitude=-122.4094
)
```

**Location Options:**
- Downtown Parking Garage
- Mall Parking Lot  
- Street Parking - Main St
- Office Building Garage
- Airport Long-term
- Hospital Visitor Parking
- University Campus
- Shopping Center
- Residential Street
- Stadium Parking

## Data Relationships

### Entity Relationship Overview
```
User (1) → (N) Car → (N) ParkingSession
     ↘                    ↗
       (1) → (N) ParkingSession
```

### Relationship Rules
1. **User → Car**: One user can own multiple cars (1-3 in mock data)
2. **User → ParkingSession**: Direct relationship for session ownership
3. **Car → ParkingSession**: Sessions are tied to specific cars
4. **Constraint**: Users can only create sessions with their own cars

## Usage Instructions

### Basic Usage
```bash
# Navigate to backend directory
cd parqr-backend

# Activate virtual environment
source .venv/bin/activate

# Run the script
python scripts/generate_mock_data.py
```

### Safety Features

**Existing Data Check:**
```
Database has 5 users. Continue? (y/N):
```
The script warns you if data already exists and asks for confirmation.

**Error Handling:**
- Automatic rollback on errors
- Database session cleanup
- Detailed error messages

### Generated Output Example
```
🚀 Starting mock data generation...
✅ Created 15 mock users
✅ Created 32 mock cars
✅ Created 75 mock parking sessions

📊 Database Summary:
   Users: 15
   Cars: 32
   Total Sessions: 75
   Active Sessions: 23
   Completed Sessions: 52

✅ Mock data generation completed!
```

## Data Quality Features

### 1. Uniqueness Validation
- **Phone Numbers**: Checked against existing database + in-memory tracking
- **User Codes**: Database collision detection with regeneration
- **License Plates**: Database collision detection with regeneration
- **QR Code IDs**: SHA-256 with UUID ensures uniqueness

### 2. Realistic Data Patterns
- **Phone Numbers**: Valid Korean mobile format with +82 country code
- **Geographic Coordinates**: Clustered in Seoul metropolitan area
- **Time Distribution**: Realistic parking patterns over 30 days
- **Session Duration**: 1-8 hour range typical for parking

### 3. Database Consistency
- **Timezone Handling**: All timestamps use UTC
- **Foreign Key Integrity**: All relationships properly maintained
- **Model Compliance**: Uses exact same validation as production routes

## Testing Scenarios Covered

### User Registration Testing
- Multiple users with unique phone numbers
- Proper user code generation
- QR code ID generation and uniqueness

### Car Management Testing  
- Multi-car ownership scenarios
- License plate uniqueness across all users
- Brand/model data variety

### Parking Session Testing
- Active vs completed sessions
- Time-based queries (recent, historical)
- User parking history
- Car usage patterns
- Geographic location data

## Customization Options

### Modify Generation Counts
```python
# In main() function
users = create_mock_users(db, count=20)        # Default: 15
cars = create_mock_cars(db, users, cars_per_user=4)  # Default: 3
create_mock_parking_sessions(db, users, cars, sessions_count=100)  # Default: 75
```

### Add Custom Locations
```python
locations = [
    "Your Custom Location",
    "Another Test Venue",
    # ... existing locations
]
```

### Adjust Geographic Area
```python
# Change coordinate ranges
lat_range = (35.1, 35.2)  # Busan coordinates
lng_range = (129.0, 129.1)
# Or
lat_range = (37.4, 37.7)  # Seoul coordinates (default)
lng_range = (126.8, 127.2)
```

### Modify Session Completion Rate
```python
# Change from 70% to different completion rate
if random.random() < 0.8:  # 80% completion rate
    end_time = start_time + timedelta(...)
```

## Integration with Application

### API Testing
The generated data is perfect for testing all your API endpoints:

- **User Registration**: Already populated users for conflict testing
- **Car Registration**: Test with existing and new license plates
- **Parking Sessions**: Mix of active and completed sessions
- **QR Code Lookups**: Realistic QR code IDs for scanning tests

### Database Performance Testing
With 75+ sessions and proper indexes, you can test:
- Query performance on foreign key relationships
- Time-based filtering and sorting
- Geographic queries with lat/lng data

### Frontend Development
Provides realistic data for UI development:
- User profiles with multiple cars
- Parking history with various durations
- Geographic visualization of parking locations
- Active vs completed session states

## Troubleshooting

### Common Issues

**"Phone number already registered" Error:**
- Increase the phone number range in `generate_phone_number()` (Korean mobile range: +821000000000 to +821099999999)
- The script now includes collision detection

**Database Connection Error:**
- Ensure your `.env` file is properly configured
- Check that MySQL is running: `brew services start mysql`
- Verify database exists: `mysql -u parqr_admin -p parqr_db`

**Import Error:**
- Make sure you're in the `parqr-backend` directory
- Activate virtual environment: `source .venv/bin/activate`
- Install dependencies: `pip install -r requirements.txt`

### Clean Database for Fresh Start
```sql
-- Connect to MySQL
mysql -u parqr_admin -p parqr_db

-- Clear all data (preserves structure)
DELETE FROM parking_sessions;
DELETE FROM cars;
DELETE FROM users;
```

## Best Practices

### Development Workflow
1. **Start Clean**: Clear existing data for consistent tests
2. **Run Script**: Generate fresh mock data
3. **Test Features**: Use realistic data for development
4. **Repeat**: Regenerate when schema changes

### Production Safety
- **Never run in production**: Script is for development only
- **Environment Check**: Verify `ENVIRONMENT=development` in `.env`
- **Data Backup**: Always backup before running in any shared environment

---

This mock data generator ensures your parQR application is tested with realistic, comprehensive data that matches production patterns and constraints.