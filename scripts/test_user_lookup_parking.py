#!/usr/bin/env python3
"""
Test script for user lookup endpoint with parking status
Sprint 9 - Testing on Cloud Deployment
"""

import requests
import json
from datetime import datetime
import sys

def load_service_url():
    """Load service URL from deployment vars"""
    try:
        with open("deployment-vars.sh", "r") as f:
            for line in f:
                if line.startswith("SERVICE_URL="):
                    return line.split("=")[1].strip().strip('"')
    except FileNotFoundError:
        return None
    return None

# Configuration - Use Cloud Run URL
BASE_URL = load_service_url()
if not BASE_URL:
    print("❌ SERVICE_URL not found. Deploy to Cloud Run first.")
    sys.exit(1)

TEST_USER_CODE = None  # Will be set after finding test user

def get_test_user():
    """Get a test user from the cloud database"""
    print("\n🔍 Finding test user in cloud database...")
    
    # Try common patterns or manually set your user code here
    test_codes = ["ABC12345", "USR00001"]  # Replace with actual user codes
    
    for code in test_codes:
        response = requests.get(f"{BASE_URL}/api/v01/user/lookup/{code}")
        if response.status_code == 200:
            global TEST_USER_CODE
            TEST_USER_CODE = code
            print(f"✅ Found test user: {code}")
            return response.json()
    
    print("❌ No test user found. Please update test_codes list with actual user codes.")
    return None

def test_user_without_parking(user_data):
    """Test user lookup when user is not parking"""
    print("\n🧪 Testing user lookup WITHOUT active parking...")
    
    response = requests.get(f"{BASE_URL}/api/v01/user/lookup/{TEST_USER_CODE}")
    
    if response.status_code == 200:
        data = response.json()
        
        # Verify parking status fields exist
        assert "parking_status" in data, "❌ Missing parking_status field"
        assert "public_message" in data, "❌ Missing public_message field"
        
        print("✅ User without parking test passed")
        print(f"   - Parking status: {data['parking_status']}")
        print(f"   - Public message: {data['public_message']}")
        print(f"   - User ID: {data['id']}")
        print(f"   - Cars: {len(data['cars'])}")
        
        return data
    else:
        print(f"❌ Failed to lookup user: {response.status_code}")
        print(response.text)
        return None

def manual_parking_session_instructions(user_id, car_id):
    """Provide SQL instructions to create test parking session in Cloud SQL"""
    print("\n" + "=" * 60)
    print("📋 MANUAL STEP: Create Active Parking Session in Cloud SQL")
    print("=" * 60)
    print("\nConnect to Cloud SQL and run this SQL:")
    print("# First, start Cloud SQL Proxy:")
    print("source deployment-vars.sh")
    print("cloud-sql-proxy --port 3307 parqr-mvp:$REGION:$DB_INSTANCE_NAME &")
    print("\n# Then connect and run SQL:")
    print(f"mysql -h 127.0.0.1 -P 3307 -u root -p$DB_ROOT_PASSWORD parqr")
    print(f"""
INSERT INTO parking_sessions 
(user_id, car_id, start_time, note_location, public_message, end_time)
VALUES 
({user_id}, {car_id}, NOW(), 'Test Location - Section A', 'Sprint 9 Test - Back by 3PM!', NULL);
""")
    print("\nPress Enter after running the SQL to continue testing...")
    input()

def test_user_with_parking():
    """Test user lookup when user has active parking"""
    print("\n🧪 Testing user lookup WITH active parking...")
    
    response = requests.get(f"{BASE_URL}/api/v01/user/lookup/{TEST_USER_CODE}")
    
    if response.status_code == 200:
        data = response.json()
        
        # Verify parking status fields
        print(f"   - Parking status: {data['parking_status']}")
        print(f"   - Public message: {data['public_message']}")
        
        if data['parking_status'] == 'active':
            print("✅ User with parking test passed")
            if data['public_message']:
                print(f"   - Public message correctly displayed: '{data['public_message']}'")
        else:
            print("⚠️  Warning: parking_status is still 'not_parked'")
            print("   Make sure the parking session was created with end_time=NULL")
    else:
        print(f"❌ Failed to lookup user: {response.status_code}")
        print(response.text)

def main():
    print("=" * 60)
    print("Sprint 9 - User Lookup Parking Status Test (Cloud)")
    print(f"Testing against: {BASE_URL}")
    print("=" * 60)
    
    # Find a test user
    user_data = get_test_user()
    if not user_data:
        print("\n⚠️  Please ensure test users exist in cloud database")
        sys.exit(1)
    
    # Test 1: User without parking
    updated_data = test_user_without_parking(user_data)
    
    if updated_data and updated_data['cars']:
        user_id = updated_data['id']
        car_id = updated_data['cars'][0]['id']
        
        # Provide SQL instructions for cloud
        manual_parking_session_instructions(user_id, car_id)
        
        # Test 2: User with parking
        test_user_with_parking()
    
    print("\n" + "=" * 60)
    print("✅ All cloud user lookup parking tests completed!")
    print("=" * 60)

if __name__ == "__main__":
    main()