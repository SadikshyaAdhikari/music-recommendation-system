# 🎵 Music Recommendation System - Complete Setup Guide

This guide will help you set up the database for this project. You have **two options**:
1. **Using Docker** (Recommended for beginners - easier and cleaner)
2. **Using Local MySQL** (If you already have MySQL installed on your computer)

---

## 📋 Option 1: Using Docker (Recommended)

Docker makes it easy to run MySQL without installing it on your computer. Think of it as running MySQL in a "virtual box" on your computer.

### Step 1: Install Docker Desktop

1. **Download Docker Desktop:**
   - Go to: https://www.docker.com/products/docker-desktop
   - Click "Download for Windows" (or Mac/Linux if you're using those)
   - The file will be named something like `Docker Desktop Installer.exe`

2. **Install Docker Desktop:**
   - Double-click the downloaded file
   - Follow the installation wizard
   - When it asks, make sure to check "Use WSL 2 instead of Hyper-V" (if on Windows)
   - Restart your computer if prompted

3. **Start Docker Desktop:**
   - After installation, open Docker Desktop from your Start Menu
   - Wait for it to fully start (you'll see a green icon in the system tray when it's ready)
   - This might take a few minutes the first time

### Step 2: Verify Docker is Working

Open PowerShell or Command Prompt and type:
```powershell
docker --version
```

You should see something like: `Docker version 24.0.0, build ...`

If you get an error, make sure Docker Desktop is running.

### Step 3: Start MySQL Database with Docker

1. **Open PowerShell in your project folder:**
   - Navigate to your project folder: `d:\python projects\music-recommendation-system`
   - Or open PowerShell there by:
     - Right-click the folder in File Explorer
     - Select "Open in Terminal" or "Open PowerShell window here"

2. **Start the MySQL database:**
   ```powershell
   docker-compose up -d
   ```

   **What this does:**
   - Downloads MySQL 8.0 (first time only - this might take a few minutes)
   - Creates a MySQL container named `music_recommendation_mysql`
   - Sets up the database `music_recommendation_db`
   - Sets the password to `rootpassword`
   - Starts MySQL in the background

3. **Check if it's running:**
   ```powershell
   docker ps
   ```
   
   You should see a container named `music_recommendation_mysql` with status "Up".

### Step 4: Verify Database Connection

Your app is already configured to use Docker MySQL! Just run:
```powershell
py app.py
```

The app should connect to the database automatically.

### Docker Commands You'll Need

| Task | Command |
|------|---------|
| Start MySQL | `docker-compose up -d` |
| Stop MySQL | `docker-compose down` |
| Restart MySQL | `docker-compose restart` |
| View logs | `docker-compose logs mysql` |
| Stop and delete all data | `docker-compose down -v` |
| Check if running | `docker ps` |

### Database Credentials (Already Configured)

- **Host:** `localhost`
- **Port:** `3306`
- **Database:** `music_recommendation_db`
- **Username:** `root`
- **Password:** `rootpassword`

**You don't need to change anything in the code!** It's already set up to use these credentials.

---

## 📋 Option 2: Using Local MySQL (Without Docker)

If you already have MySQL installed on your computer, or prefer not to use Docker, follow these steps.

### Step 1: Install MySQL (If Not Already Installed)

1. **Download MySQL Installer:**
   - Go to: https://dev.mysql.com/downloads/installer/
   - Download "MySQL Installer for Windows"
   - Choose the "Full" option (or "Custom" if you want to select components)

2. **Install MySQL:**
   - Run the installer
   - Choose "Developer Default" setup type
   - Complete the installation wizard
   - **IMPORTANT:** Remember the root password you set during installation!

3. **Start MySQL Service:**
   - Press `Win + R`, type `services.msc`, press Enter
   - Find "MySQL80" in the list
   - Right-click and select "Start" (if not already started)

### Step 2: Create the Database

1. **Open MySQL Command Line Client** (or MySQL Workbench)

2. **Login:**
   ```sql
   mysql -u root -p
   ```
   Enter your MySQL root password when prompted.

3. **Create the database:**
   ```sql
   CREATE DATABASE music_recommendation_db;
   EXIT;
   ```

### Step 3: Edit the Code Configuration

You need to update `app.py` to use your local MySQL credentials.

**Open `app.py` and find these lines (around line 28-35):**

```python
# Database configuration
# Uses environment variables if set, otherwise defaults to Docker MySQL values
DB_CONFIG = {
    'host': os.getenv('MYSQL_HOST', 'localhost'),
    'database': os.getenv('MYSQL_DATABASE', 'music_recommendation_db'),
    'user': os.getenv('MYSQL_USER', 'root'),
    'password': os.getenv('MYSQL_PASSWORD', 'rootpassword'),  # Default Docker MySQL password
}
```

**Change it to match your local MySQL setup:**

```python
# Database configuration for LOCAL MySQL
DB_CONFIG = {
    'host': 'localhost',           # Keep this as localhost
    'database': 'music_recommendation_db',  # The database you created
    'user': 'root',                 # Your MySQL username (usually 'root')
    'password': 'YOUR_MYSQL_PASSWORD',  # ⚠️ CHANGE THIS to your actual MySQL root password
}
```

**Example:**
If your MySQL root password is `MyPassword123`, change it to:
```python
'password': 'MyPassword123',  # Your local MySQL password
```

### Step 4: Update docker-compose.yml (Optional)

If you're using local MySQL, you can ignore the `docker-compose.yml` file. Or, to avoid confusion, you can add a comment at the top:

```yaml
# NOT USED - Using Local MySQL instead
# To use Docker MySQL, uncomment below and edit app.py accordingly
# services:
#   mysql:
#     ...
```

---

## 🐛 Troubleshooting

### Problem: Docker Desktop won't start

**Solutions:**
1. Make sure virtualization is enabled in your BIOS
2. On Windows, make sure WSL 2 is installed:
   ```powershell
   wsl --install
   ```
3. Restart your computer after installing WSL 2

### Problem: Port 3306 is already in use

This means you already have MySQL running on your computer.

**Option A:** Stop your local MySQL service:
```powershell
# In PowerShell as Administrator
Stop-Service MySQL80
```

**Option B:** Use a different port in Docker:
1. Open `docker-compose.yml`
2. Change `"3306:3306"` to `"3307:3306"` on the ports line:
   ```yaml
   ports:
     - "3307:3306"  # Changed from 3306:3306
   ```
3. Update `app.py` DB_CONFIG:
   ```python
   DB_CONFIG = {
       'host': 'localhost',
       'port': 3307,  # Add this line
       'database': 'music_recommendation_db',
       'user': 'root',
       'password': 'rootpassword',
   }
   ```

### Problem: Cannot connect to MySQL

**Check these:**
1. Is MySQL running? (Check with `docker ps` for Docker, or check Windows Services for local MySQL)
2. Are the credentials correct? (Check `app.py` DB_CONFIG)
3. Is the database created? (For local MySQL, make sure you created the database)

**For Docker:**
```powershell
# Check if container is running
docker ps

# Check logs for errors
docker-compose logs mysql

# Restart MySQL
docker-compose restart
```

**For Local MySQL:**
```powershell
# Check if service is running (in PowerShell as Administrator)
Get-Service MySQL80

# Start service if stopped
Start-Service MySQL80
```

### Problem: docker-compose command not found

This means Docker Compose isn't installed or isn't in your PATH.

**Solution:**
- Make sure Docker Desktop is fully installed and running
- Restart PowerShell/Command Prompt after installing Docker
- Try using: `docker compose up -d` (without the hyphen) - newer Docker versions use this

### Problem: Database connection error in app.py

**Common causes:**
1. MySQL not running (see above)
2. Wrong password in `app.py` DB_CONFIG
3. Database doesn't exist (for local MySQL)

**Fix:**
- Double-check your `app.py` DB_CONFIG section
- Make sure passwords match
- For local MySQL, verify the database exists:
  ```sql
  SHOW DATABASES;
  ```

---

## 📝 Quick Reference

### Using Docker (Easiest)
```powershell
# Start database
docker-compose up -d

# Run app (in another terminal)
py app.py
```

### Using Local MySQL
```python
# Edit app.py - Change DB_CONFIG password to your MySQL password
DB_CONFIG = {
    'host': 'localhost',
    'database': 'music_recommendation_db',
    'user': 'root',
    'password': 'YOUR_MYSQL_PASSWORD',  # Change this!
}
```

Then run:
```powershell
py app.py
```

---

## ✅ Verification Checklist

After setup, verify everything works:

- [ ] Docker Desktop is running (if using Docker)
- [ ] MySQL container is running: `docker ps` shows `music_recommendation_mysql`
- [ ] OR MySQL service is running (if using local MySQL)
- [ ] Database exists (`music_recommendation_db`)
- [ ] `app.py` has correct credentials in DB_CONFIG
- [ ] Running `py app.py` doesn't show database connection errors
- [ ] You can access the web app at `http://localhost:5000`

---

## 🎯 Which Option Should I Choose?

**Choose Docker if:**
- You're new to databases
- You want the easiest setup
- You don't want to install MySQL on your computer
- You want to keep your system clean

**Choose Local MySQL if:**
- You already have MySQL installed
- You prefer managing MySQL directly
- You need to use MySQL for other projects too

---

## 📚 Additional Resources

- **Docker Documentation:** https://docs.docker.com/
- **MySQL Documentation:** https://dev.mysql.com/doc/
- **Docker Desktop Download:** https://www.docker.com/products/docker-desktop

---

## 💡 Tips

1. **Keep Docker Desktop running** while working on the project (if using Docker)
2. **Don't change passwords** unless you also update `app.py` and `docker-compose.yml`
3. **Use `docker-compose down`** to stop MySQL when you're done working (saves resources)
4. **Check logs** if something goes wrong: `docker-compose logs mysql`

Good luck! 🚀

