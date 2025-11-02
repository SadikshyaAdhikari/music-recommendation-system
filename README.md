# Music Recommendation System

## Project Type
This is a **Flask web application** (Python web framework) that provides a music recommendation system with a web interface and REST API.

## Technologies Used
- **Flask** - Web framework
- **MySQL** - Database
- **scikit-learn** - Machine learning for recommendations (TF-IDF, Cosine Similarity)
- **NumPy** - Numerical computations

## Prerequisites
1. **Python** (3.8 or higher)
2. **MySQL Database** (via Docker or Local installation)

## 🚀 Quick Start

### For Beginners (Recommended: Docker)

**📖 For complete setup instructions, see: [SETUP_GUIDE.md](SETUP_GUIDE.md)**

The easiest way to get started:

1. **Install Docker Desktop** (if not installed)
   - Download from: https://www.docker.com/products/docker-desktop

2. **Start MySQL Database with Docker:**
   ```bash
   docker-compose up -d
   ```

3. **Install Python Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the Application:**
   ```bash
   python app.py
   ```

The app is already configured to use Docker MySQL with these credentials:
- Host: `localhost`
- Database: `music_recommendation_db`
- User: `root`
- Password: `rootpassword`

### Alternative: Using Local MySQL

If you prefer not to use Docker or already have MySQL installed:

1. **See [SETUP_GUIDE.md](SETUP_GUIDE.md)** for detailed instructions
2. Edit `app.py` (lines 28-35) to update DB_CONFIG with your MySQL credentials
3. Create the database: `CREATE DATABASE music_recommendation_db;`

### What Happens When You Run the App

The application will automatically:
- Connect to the MySQL database
- Create all required database tables
- Insert sample music data
- Start the web server at `http://localhost:5000`

## Accessing the Application
- **Web Interface**: Open `http://localhost:5000` in your browser
- **Landing Page**: `http://localhost:5000/`
- **Login/Signup**: Required to access the main features
- **Dashboard**: `http://localhost:5000/dashboard`
- **API Endpoints**: Available at `/api/*`

## API Endpoints
- `GET /api/music` - Get all music with optional filters
- `POST /api/recommend` - Get recommendations based on preferences
- `POST /api/play` - Record music play events
- `GET /api/stats` - Get system statistics
- `GET /api/health` - Health check

## Features
- User authentication (signup/login)
- Music search and browsing
- Personalized recommendations
- Favorites and playlists
- Listening history
- Admin panel for song management


