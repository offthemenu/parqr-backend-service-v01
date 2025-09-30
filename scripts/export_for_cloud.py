"""
    Export local database schema and essential data for cloud migration
"""

import subprocess
import os
from datetime import datetime

def export_schema_and_data():
    """Export database schema and essential data"""

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    export_dir = "cloud_migration"
    os.makedirs(export_dir, exist_ok=True)

    print("Exporting database schema and data...")

    # Export schema only (no data)
    schema_file = f"{export_dir}/schema_{timestamp}.sql"
    schema_cmd = [
        "mysqldump",
        "-h", "127.0.0.1",
        "-P", "3306", # 3306 when exporting from local
        "-u", "admin",
        "-p",
        "--no-data",
        "--routines",
        "--triggers",
        "parqr"
    ]

    print(f"Exporting schema to {schema_file}")
    with open(schema_file, "w") as f:
        subprocess.run(schema_cmd, stdout=f)

    # Export essential data (users, cars, parking_sessions for testing purposes)
    data_file = f"{export_dir}/test_data_{timestamp}.sql"
    data_cmd = [
        "mysqldump",
        "-h", "127.0.0.1",
        "-P", "3306",
        "-u", "admin",
        "-p",
        "--no-create-info",
        "--complete-insert",
        "--extended-insert",
        "parqr",
        "users",
        "cars",
        "parking_sessions",
        "move_requests"
    ]

    print(f"Exporting data to {data_file}")
    with open(data_file, "w") as f:
        subprocess.run(data_cmd, stdout=f)

    # Create combined file
    combined_file = f"{export_dir}/cloud_migration_{timestamp}.sql"
    print(f"Creating combined file: {combined_file}")

    with open(combined_file, "w") as outfile:
        # Add header
        outfile.write("-- ParQR Cloud Migration Export\n")
        outfile.write(f"-- Generated: {datetime.now()}\n")
        outfile.write("-- ================================\n\n")
        
        # Add schema
        with open(schema_file, "r") as infile:
            outfile.write("-- SCHEMA\n")
            outfile.write(infile.read())
            
        # Add data
        with open(data_file, "r") as infile:
            outfile.write("\n\n-- TEST DATA\n")
            outfile.write(infile.read())
    
    print(f"✅ Export complete: {combined_file}")
    return combined_file

if __name__ == "__main__":
    export_file = export_schema_and_data()
    print(f"\nUse this file for cloud import: {export_file}")