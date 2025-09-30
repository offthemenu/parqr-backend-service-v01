# parQR Database Setup Guide for macOS

This guide provides a streamlined approach to setting up the parQR database on macOS machines using MySQL. This setup is designed for easy reinitialization across multiple Mac devices - simply follow this guide and run `alembic upgrade head` to get up and running quickly.

## Table of Contents

1. [Quick Setup for Multiple Macs](#quick-setup-for-multiple-macs)
2. [Prerequisites](#prerequisites)
3. [MySQL Installation and Setup](#mysql-installation-and-setup)
4. [Database and User Creation](#database-and-user-creation)
5. [Project Setup](#project-setup)
6. [Environment Configuration](#environment-configuration)
7. [Python Environment and Dependencies](#python-environment-and-dependencies)
8. [Database Schema Migration](#database-schema-migration)
9. [Verification](#verification)
10. [Troubleshooting](#troubleshooting)

## Quick Setup for Multiple Macs

If you're setting up parQR on a new Mac and have already configured it on another machine, here's the streamlined workflow:

1. **Install prerequisites** (see below)
2. **Set up MySQL** with the same database name, user, and password as your other machines
3. **Clone the repository and configure environment**
4. **Install Python dependencies**
5. **Run `alembic upgrade head`** to apply all migrations

This approach ensures all configurations, models, and schemas are consistent across your Mac devices.

## Prerequisites

**Required Software:**
- **Homebrew** (macOS package manager)
- **Python 3.8+** 
- **MySQL 8.0+**
- **Git**

**Install Homebrew** (if not already installed):
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

**Install all prerequisites:**
```bash
# Install core dependencies
brew install python3 git mysql pkg-config mysql-client

# Add MySQL client to PATH (add this to your ~/.zshrc or ~/.bash_profile)
echo 'export PATH="/opt/homebrew/bin:$PATH"' >> ~/.zshrc
echo 'export PATH="/opt/homebrew/opt/mysql-client/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

## MySQL Installation and Setup

### 1. Start MySQL Service
```bash
# Start MySQL service
brew services start mysql

# Verify MySQL is running
brew services list | grep mysql
```

### 2. Secure MySQL Installation
```bash
mysql_secure_installation
```

Follow the prompts:
- **Set root password** (choose a strong password)
- **Remove anonymous users** → Yes
- **Disallow root login remotely** → Yes  
- **Remove test database** → Yes
- **Reload privilege tables** → Yes

## Database and User Creation

**Important:** Use the same database credentials across all your Mac devices for consistency.

Connect to MySQL as root:
```bash
mysql -u root -p
```

Create the database and user:
```sql
-- Create database with proper character set
CREATE DATABASE parqr_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Create dedicated user (use the same password across all your Mac devices)
CREATE USER 'admin'@'localhost' IDENTIFIED BY 'SQL-parqr-wkddusdn1!';

-- Grant all privileges
GRANT ALL PRIVILEGES ON parqr_db.* TO 'admin'@'localhost';

-- Apply changes
FLUSH PRIVILEGES;

-- Verify database was created
SHOW DATABASES;

-- Exit MySQL
EXIT;
```

**Test the connection:**
```bash
mysql -u admin -p parqr_db
```

Or using TCP connection (if socket issues):
```bash
mysql -u admin -h 127.0.0.1 -P 3306 -p parqr_db
```
Type `EXIT;` to quit once you confirm the connection works.

## Project Setup

### 1. Clone the Repository
```bash
# Clone to your preferred location
git clone <repository-url>
cd parQR-mvp/parqr-backend
```

## Environment Configuration

**Important:** Use the exact same `.env` configuration across all your Mac devices.

### 1. Create Environment File
```bash
# Create .env file
touch .env

# Set secure permissions
chmod 600 .env
```

### 2. Configure Environment Variables

Add this configuration to `.env` (replace `your_secure_password` with your actual password):

```bash
# Database Configuration
DB_USER=admin
DB_PASSWORD=SQL-parqr-wkddusdn1!
DB_HOST=localhost
DB_PORT=3306
DB_NAME=parqr_db

# Database URL (automatically constructed)
DATABASE_URL=mysql+mysqldb://admin:SQL-parqr-wkddusdn1!@localhost:3306/parqr_db

# Application Settings
ENVIRONMENT=development
DEBUG=True
```

**Note:** The `.env` file is already in `.gitignore` and won't be committed to version control.

## Python Environment and Dependencies

### 1. Create and Activate Virtual Environment
```bash
# Create virtual environment
python3 -m venv parqr_env

# Activate it
source parqr_env/bin/activate

# Your terminal prompt should now show (parqr_env)
```

### 2. Install Dependencies
```bash
# Upgrade pip
pip install --upgrade pip

# Install all project dependencies
pip install -r requirements.txt
```

### 3. Verify Setup
```bash
# Test environment configuration
python3 -c "
import os
from dotenv import load_dotenv
load_dotenv()
print('✅ DB_USER:', os.getenv('DB_USER'))
print('✅ DB_HOST:', os.getenv('DB_HOST'))
print('✅ Environment loaded successfully')
"
```

## Database Schema Migration

This is the key step that makes working across multiple Macs simple - Alembic will automatically create all tables and apply all schema updates.

### 1. Test Database Connection
```bash
# Verify connection to your database
python3 -c "
from app.db.session import engine
try:
    connection = engine.connect()
    print('✅ Database connection successful!')
    connection.close()
except Exception as e:
    print('❌ Database connection failed:', e)
"
```

### 2. Apply All Migrations
This single command will create all tables and apply all schema changes:

```bash
# Apply all migrations to bring database up to current schema
alembic upgrade head
```

You should see output like:
```
INFO  [alembic.runtime.migration] Context impl MySQLImpl.
INFO  [alembic.runtime.migration] Will assume non-transactional DDL.
INFO  [alembic.runtime.migration] Running upgrade  -> 85b89fa95f39, Initial schema reset
INFO  [alembic.runtime.migration] Running upgrade 85b89fa95f39 -> 86041de9befc, Add longitude and latitude to parking sessions
```

### 3. Verify Migration Status
```bash
# Check current database revision
alembic current

# Should show the latest migration ID
```

## MySQL Workbench Setup (Optional)

MySQL Workbench provides a graphical interface to manage your parQR database, making it easier to view data, run queries, and debug issues.

### Installation

```bash
# Install MySQL Workbench via Homebrew
brew install --cask mysqlworkbench

# Or download from: https://dev.mysql.com/downloads/workbench/
```

### Creating a Connection

1. **Open MySQL Workbench**

2. **Create New Connection**:
   - Click the `+` icon next to "MySQL Connections"
   - Or go to `Database` → `Manage Connections`

3. **Configure Connection Settings**:
   ```
   Connection Name: parQR Local Database
   Connection Method: Standard (TCP/IP)
   Hostname: 127.0.0.1
   Port: 3306
   Username: admin
   Default Schema: parqr_db
   ```

4. **Set Password**:
   - Click "Store in Vault..." (macOS) or "Store in Keychain..."
   - Enter password: `SQL-parqr-wkddusdn1!`
   - Click "OK"

5. **Advanced Settings** (Optional but Recommended):
   - Click "Advanced" tab
   - Set "Use SSL": `No` (since it's localhost)
   - Set "SQL_MODE": Leave default or set to `TRADITIONAL`

6. **Test Connection**:
   - Click "Test Connection" button
   - Should display: "Successfully made the MySQL connection"
   - If it fails, verify MySQL is running: `brew services list | grep mysql`

7. **Save Connection**:
   - Click "OK" to save the connection
   - You'll see "parQR Local Database" in your connections list

### Connecting and Using Workbench

1. **Connect**: Double-click your "parQR Local Database" connection

2. **Navigate Database**:
   - Left sidebar shows "SCHEMAS"
   - Expand `parqr_db` to see tables:
     - `users`
     - `cars`
     - `parking_sessions`
     - `alembic_version`

3. **Useful Features**:
   
   **View Table Data**:
   - Right-click any table → "Select Rows - Limit 1000"
   
   **Run Custom Queries**:
   ```sql
   -- Show all tables
   SHOW TABLES;
   
   -- View table structures
   DESCRIBE users;
   DESCRIBE cars;
   DESCRIBE parking_sessions;
   
   -- Check data counts
   SELECT 
       (SELECT COUNT(*) FROM users) as total_users,
       (SELECT COUNT(*) FROM cars) as total_cars,
       (SELECT COUNT(*) FROM parking_sessions) as total_sessions;
   
   -- View recent parking sessions with user details
   SELECT 
       ps.id,
       u.phone_number,
       c.license_plate,
       ps.start_time,
       ps.end_time,
       ps.note_location
   FROM parking_sessions ps
   JOIN users u ON ps.user_id = u.id
   JOIN cars c ON ps.car_id = c.id
   ORDER BY ps.start_time DESC
   LIMIT 10;
   ```

   **Export Data**:
   - Right-click table → "Table Data Export Wizard"
   
   **Visual Query Builder**:
   - Use the visual query builder for complex queries

### Troubleshooting Workbench Connection

#### Connection Fails
```bash
# Verify MySQL is running
brew services list | grep mysql

# If not running, start it
brew services start mysql

# Test command line connection first
mysql -u admin -h 127.0.0.1 -P 3306 -p parqr_db
```

#### "Access Denied" Error
- Double-check username: `admin`
- Double-check password: `SQL-parqr-wkddusdn1!`
- Verify user exists:
```sql
mysql -u root -h 127.0.0.1 -P 3306 -e "SELECT User, Host FROM mysql.user WHERE User='admin';"
```

#### "Unknown Database" Error
- Verify database exists:
```sql
mysql -u root -h 127.0.0.1 -P 3306 -e "SHOW DATABASES;"
```
- If `parqr_db` is missing, recreate it using the database reset instructions above

#### SSL Connection Issues
- In Workbench connection settings, set "Use SSL" to "No"
- Or use "Require" and configure SSL certificates if needed

### Workbench Best Practices

1. **Use Transactions for Data Changes**:
   ```sql
   START TRANSACTION;
   -- Your data modification queries here
   -- COMMIT; -- Only run this if you're sure
   ROLLBACK; -- Use this to undo changes
   ```

2. **Backup Before Major Changes**:
   - Server → Data Export → Select `parqr_db` → Export

3. **Monitor Query Performance**:
   - Use "Query" → "Explain Current Statement" for slow queries

4. **View Migration History**:
   ```sql
   SELECT * FROM alembic_version;
   ```

## Verification

### 1. Check Database Tables
```bash
# Verify all tables were created
mysql -u admin -p parqr_db -e "SHOW TABLES;"

# Or using TCP connection if socket issues:
mysql -u admin -h 127.0.0.1 -P 3306 -p parqr_db -e "SHOW TABLES;"
```

You should see:
```
+------------------+
| Tables_in_parqr_db |
+------------------+
| alembic_version   |
| cars             |
| parking_sessions |
| users            |
+------------------+
```

### 2. Verify Table Structure
```bash
# Check key table structures
mysql -u admin -p parqr_db -e "
DESCRIBE users;
DESCRIBE cars; 
DESCRIBE parking_sessions;
"

# Or using TCP connection:
mysql -u admin -h 127.0.0.1 -P 3306 -p parqr_db -e "DESCRIBE parking_sessions;"
```

### 3. Test Application Connection
```bash
# Test that the application can connect to the database
python3 -c "
from app.db.session import SessionLocal
from app.models.user import User
from app.models.car import Car
from app.models.parking_session import ParkingSession

db = SessionLocal()
try:
    user_count = db.query(User).count()
    car_count = db.query(Car).count()
    session_count = db.query(ParkingSession).count()
    print(f'✅ Database connection successful!')
    print(f'Users: {user_count}, Cars: {car_count}, Sessions: {session_count}')
finally:
    db.close()
"
```

## Working with Multiple Mac Devices

### Adding a New Mac Device

When you want to work on parQR from a new Mac:

1. **Follow this guide** from the beginning
2. **Use identical credentials** (same DB_USER, DB_PASSWORD, DB_NAME)
3. **Run `alembic upgrade head`** to get the latest schema
4. **You're ready to go!**

### Keeping Devices in Sync

When you pull new code with database changes:

```bash
# Pull latest code
git pull origin main

# Apply any new migrations
alembic upgrade head

# Verify current state
alembic current
```

## Complete Database Reset (Nuclear Option)

If you encounter persistent database issues, corrupted migrations, or want a completely fresh start, follow these steps:

### Option 1: Reset with MySQL Reinstall (Recommended for Clean State)

```bash
# 1. Stop MySQL service
brew services stop mysql

# 2. Completely uninstall MySQL
brew uninstall mysql

# 3. Remove MySQL data directory
rm -rf /opt/homebrew/var/mysql

# 4. Reinstall MySQL (fresh install, no root password)
brew install mysql

# 5. Start MySQL
brew services start mysql

# 6. Create database and user
mysql -u root -e "
CREATE USER 'admin'@'localhost' IDENTIFIED BY 'SQL-parqr-wkddusdn1!';
CREATE DATABASE parqr_db;
GRANT ALL PRIVILEGES ON parqr_db.* TO 'admin'@'localhost';
FLUSH PRIVILEGES;
"

# 7. Apply all migrations
alembic upgrade head

# 8. Verify setup
alembic current
mysql -u admin -h 127.0.0.1 -P 3306 -p parqr_db -e "SHOW TABLES;"
```

### Option 2: Reset Database Only (Keep MySQL Installation)

```bash
# 1. Connect to MySQL as root
mysql -u root -h 127.0.0.1 -P 3306 -e "
DROP DATABASE IF EXISTS parqr_db;
DROP USER IF EXISTS 'admin'@'localhost';
CREATE USER 'admin'@'localhost' IDENTIFIED BY 'SQL-parqr-wkddusdn1!';
CREATE DATABASE parqr_db;
GRANT ALL PRIVILEGES ON parqr_db.* TO 'admin'@'localhost';
FLUSH PRIVILEGES;
"

# 2. Reset Alembic migration history
# (This tells Alembic to start fresh)
rm -f alembic/versions/*.pyc
rm -rf alembic/versions/__pycache__

# 3. Apply all migrations from scratch
alembic upgrade head

# 4. Verify everything is working
alembic current
mysql -u admin -h 127.0.0.1 -P 3306 -p parqr_db -e "SHOW TABLES; DESCRIBE parking_sessions;"
```

### Option 3: Reset Alembic Only (Keep Database Structure)

If only migration history is corrupted but database structure is correct:

```bash
# 1. Reset alembic version tracking
mysql -u admin -h 127.0.0.1 -P 3306 -p parqr_db -e "DROP TABLE IF EXISTS alembic_version;"

# 2. Mark current state as latest migration
alembic stamp head

# 3. Verify current state
alembic current
```

### When to Use Each Option

- **Option 1**: Use when you have forgotten MySQL root password, have socket connection issues, or want the cleanest possible setup
- **Option 2**: Use when MySQL works fine but database/user setup is corrupted
- **Option 3**: Use when database structure is correct but Alembic thinks migrations are out of sync

## Troubleshooting

### Common macOS Issues

#### 1. MySQL Won't Start
```bash
# Check if MySQL is running
brew services list | grep mysql

# Start MySQL if not running
brew services start mysql

# If still having issues, try restarting
brew services restart mysql
```

#### 2. Can't Connect to MySQL / Socket Issues
```bash
# Check if MySQL is running and listening
brew services list | grep mysql
lsof -i :3306

# Try TCP connection instead of socket
mysql -u admin -h 127.0.0.1 -P 3306 -p parqr_db

# If socket connection fails, always use TCP in .env:
# DATABASE_URL=mysql+mysqldb://admin:SQL-parqr-wkddusdn1!@127.0.0.1:3306/parqr_db

# Check user permissions:
mysql -u root -h 127.0.0.1 -P 3306 -e "SELECT User, Host FROM mysql.user WHERE User='admin';"

# If access denied, recreate user:
mysql -u root -h 127.0.0.1 -P 3306 -e "
DROP USER IF EXISTS 'admin'@'localhost';
CREATE USER 'admin'@'localhost' IDENTIFIED BY 'SQL-parqr-wkddusdn1!';
GRANT ALL PRIVILEGES ON parqr_db.* TO 'admin'@'localhost';
FLUSH PRIVILEGES;
"
```

#### 3. mysqlclient Installation Problems
```bash
# Make sure MySQL client is in PATH
export PATH="/opt/homebrew/opt/mysql-client/bin:$PATH"

# Reinstall mysqlclient if needed
pip uninstall mysqlclient
pip install mysqlclient

# If still failing, try:
brew install pkg-config mysql-client
pip install mysqlclient
```

#### 4. Alembic Migration Issues

**Common Alembic problems and solutions:**

```bash
# Problem: "Table doesn't exist" during migration
# Solution: Reset alembic and start fresh
mysql -u admin -h 127.0.0.1 -P 3306 -p parqr_db -e "DROP TABLE IF EXISTS alembic_version;"
alembic upgrade head

# Problem: "Duplicate column name" during migration  
# Solution: Skip problematic migration
alembic stamp <migration_id_to_skip>
alembic upgrade head

# Problem: Initial migration is empty (just 'pass')
# This means you need to edit the initial migration file to create tables
# See: alembic/versions/85b89fa95f39_initial_schema_reset.py

# Problem: Migration order is wrong
# Check migration history and dependencies:
alembic history
alembic show <migration_id>

# Problem: Database exists but alembic thinks it's empty
alembic stamp head  # Mark as current
alembic current     # Verify

# Problem: Want to start completely fresh
# See "Complete Database Reset" section above
```

**Debugging Alembic Issues:**
```bash
# Check what Alembic thinks the current state is
alembic current

# Check the full migration history
alembic history --verbose

# Show details of a specific migration
alembic show 85b89fa95f39

# Check what changes Alembic would make (dry run)
alembic upgrade head --sql

# Manually fix migration state if needed
alembic stamp <correct_migration_id>
```

#### 5. Virtual Environment Issues
```bash
# Deactivate and recreate if having Python issues
deactivate
rm -rf parqr_env
python3 -m venv parqr_env
source parqr_env/bin/activate
pip install -r requirements.txt
```

#### 6. Permission Denied Errors
```bash
# Fix .env file permissions
chmod 600 .env

# Fix MySQL data directory permissions (if needed)
sudo chown -R $(whoami) /opt/homebrew/var/mysql
```

### Quick Recovery Commands

If something goes wrong, here are the fastest recovery steps:

```bash
# 1. Complete reset (nuclear option)
brew services stop mysql
brew uninstall mysql
rm -rf /opt/homebrew/var/mysql
brew install mysql
brew services start mysql

# 2. Recreate database and user
mysql -u root -h 127.0.0.1 -P 3306 -e "
CREATE USER 'admin'@'localhost' IDENTIFIED BY 'SQL-parqr-wkddusdn1!';
CREATE DATABASE parqr_db;
GRANT ALL PRIVILEGES ON parqr_db.* TO 'admin'@'localhost';
FLUSH PRIVILEGES;
"

# 3. Apply all migrations
alembic upgrade head

# 4. Verify everything is working
alembic current
mysql -u admin -h 127.0.0.1 -P 3306 -p parqr_db -e "SHOW TABLES;"
python3 -c "from app.db.session import SessionLocal; print('✅ Database ready!')"
```

### Key Points for Success

1. **Always use TCP connections** (`127.0.0.1:3306`) instead of socket connections to avoid socket issues
2. **Use consistent credentials** across all Mac devices: 
   - User: `admin`
   - Password: `SQL-parqr-wkddusdn1!`
   - Database: `parqr_db`
3. **Let Alembic handle schema**: Run `alembic upgrade head` to apply all migrations automatically
4. **When in doubt, reset completely**: Use Option 1 in the "Complete Database Reset" section for a guaranteed clean state

---

**That's it!** This comprehensive guide covers everything from basic setup to complete troubleshooting. The database setup process we just went through (MySQL reset + Alembic migrations) is now documented as the standard approach for any parQR setup issues.