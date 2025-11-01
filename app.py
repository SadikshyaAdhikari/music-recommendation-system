from flask import Flask,flash, request, jsonify, render_template, redirect, url_for, session
from flask_cors import CORS
import mysql.connector
from mysql.connector import Error
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import logging
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = "mysecret123"
CORS(app)

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'database': 'music_recommendation_db',
    'user': 'root',
    'password': '',
    
}

class MusicRecommendationSystem:
    def __init__(self):
        self.connection = None
        self.vectorizer = TfidfVectorizer(stop_words='english')
        self.feature_matrix = None
        self.music_data = None
        self.initialize_database()
        
    def get_database_connection(self):
        try:
            if self.connection is None or not self.connection.is_connected():
                self.connection = mysql.connector.connect(**DB_CONFIG)
            return self.connection
        except Error as e:
            logger.error(f"Connection error: {e}")
        return None

    def initialize_database(self):
        """Initialize database tables"""
        try:
            connection = self.get_database_connection()
            if connection:
                cursor = connection.cursor()
                
                # Create users table
                create_users_table = """
                CREATE TABLE IF NOT EXISTS users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    email VARCHAR(255) UNIQUE NOT NULL,
                    password VARCHAR(255) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
       
                )
                """
                
                # Create music table
                create_music_table = """
                CREATE TABLE IF NOT EXISTS music (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    title VARCHAR(255) NOT NULL,
                    artist VARCHAR(255) NOT NULL,
                    album VARCHAR(255),
                    genre VARCHAR(100),
                    year INT,
                    duration INT,
                    audio_url VARCHAR(500),
                    features TEXT,
                    popularity_score INT DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """
                
                # Create user preferences table
                create_preferences_table = """
                CREATE TABLE IF NOT EXISTS user_preferences (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id VARCHAR(100),
                    music_id INT,
                    preference_score FLOAT DEFAULT 1.0,
                    interaction_type VARCHAR(50),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (music_id) REFERENCES music(id)
                )
                """
                
                # Create user listening history table
                create_history_table = """
                CREATE TABLE IF NOT EXISTS listening_history (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id VARCHAR(100),
                    music_id INT,
                    play_duration INT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (music_id) REFERENCES music(id)
                )
                """
                
                cursor.execute(create_users_table)
                cursor.execute(create_music_table)
                cursor.execute(create_preferences_table)
                cursor.execute(create_history_table)
                
                connection.commit()
                logger.info("Database initialized successfully")
                
        except Error as e:
            logger.error(f"Database initialization error: {e}")
    
    def insert_sample_data(self):
        """Insert sample music data"""
        try:
            connection = self.get_database_connection()
            cursor = connection.cursor()
            
            # Check if data already exists
            cursor.execute("SELECT COUNT(*) FROM music")
            count = cursor.fetchone()[0]
            
            if count == 0:
                sample_music = [
                    ("Sunset Dreams", "Luna Eclipse", "Midnight Vibes", "Electronic", 2024, 245, "", "electronic dreamy atmospheric synthwave"),
                    ("Ocean Waves", "Coastal Harmony", "Nature Sounds", "Ambient", 2023, 198, "", "ambient nature relaxing peaceful ocean"),
                    ("City Lights", "Urban Beat", "Street Symphony", "Hip Hop", 2024, 212, "", "hip hop urban beat energetic city"),
                    ("Mountain High", "Folk Tales", "Country Roads", "Folk", 2022, 267, "", "folk acoustic country storytelling mountains"),
                    ("Neon Nights", "Cyber Pulse", "Digital Dreams", "Electronic", 2024, 189, "", "electronic cyberpunk futuristic neon"),
                    ("Rainfall", "Nature's Voice", "Earth Sounds", "Ambient", 2023, 234, "", "ambient rain nature meditation calm"),
                    ("Street Dance", "Hip Hop Collective", "Urban Groove", "Hip Hop", 2024, 198, "", "hip hop dance urban energetic street"),
                    ("Countryside", "Acoustic Soul", "Rural Melodies", "Folk", 2023, 245, "", "folk acoustic rural countryside peaceful"),
                    ("Stargazing", "Cosmic Journey", "Space Odyssey", "Electronic", 2024, 278, "", "electronic space ambient cosmic stars"),
                    ("Thunder Storm", "Weather Sounds", "Natural Elements", "Ambient", 2023, 312, "", "ambient thunder storm nature dramatic"),
                    ("Breakbeat", "Electronic Fusion", "Beat Masters", "Electronic", 2024, 187, "", "electronic breakbeat energetic dance"),
                    ("Campfire Stories", "Folk Legends", "Tales of Old", "Folk", 2022, 234, "", "folk storytelling campfire acoustic warmth"),
                    ("Midnight Drive", "Retro Wave", "80s Revival", "Electronic", 2024, 198, "", "electronic retro synthwave driving midnight"),
                    ("Forest Walk", "Nature's Path", "Woodland Sounds", "Ambient", 2023, 267, "", "ambient forest nature walking peaceful"),
                    ("Urban Jungle", "City Beats", "Metropolitan", "Hip Hop", 2024, 201, "", "hip hop urban jungle city beats modern")
                ]
                
                insert_query = """
                INSERT INTO music (title, artist, album, genre, year, duration, audio_url, features)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """
                
                cursor.executemany(insert_query, sample_music)
                connection.commit()
                logger.info(f"Inserted {len(sample_music)} sample music records")
                
        except Error as e:
            logger.error(f"Sample data insertion error: {e}")
    
    def get_all_music(self, query=None, genre=None, year=None):
        """Retrieve music from database with optional filters"""
        try:
            connection = self.get_database_connection()
            cursor = connection.cursor(dictionary=True)
            
            sql = "SELECT * FROM music WHERE 1=1"
            params = []
            
            if query:
                sql += " AND (title LIKE %s OR artist LIKE %s OR album LIKE %s)"
                query_param = f"%{query}%"
                params.extend([query_param, query_param, query_param])
            
            if genre:
                sql += " AND genre LIKE %s"
                params.append(f"%{genre}%")
            
            if year:
                if year.endswith('s'):
                    if year == '90s':
                        sql += " AND year BETWEEN 1990 AND 1999"
                    elif year == '2000s':
                        sql += " AND year BETWEEN 2000 AND 2009"
                    elif year == '2010s':
                        sql += " AND year BETWEEN 2010 AND 2019"
                else:
                    sql += " AND year = %s"
                    params.append(int(year))
            
            sql += " ORDER BY popularity_score DESC, created_at DESC"
            
            cursor.execute(sql, params)
            music_list = cursor.fetchall()
            
            return music_list
            
        except Error as e:
            logger.error(f"Database query error: {e}")
            return []
    
    def build_feature_matrix(self):
        """Build TF-IDF feature matrix for cosine similarity"""
        try:
            music_data = self.get_all_music()
            if not music_data:
                return None
            
            feature_texts = []
            for music in music_data:
                features = music.get('features', '')
                genre = music.get('genre', '').lower()
                artist = music.get('artist', '').lower()
                combined_features = f"{features} {genre} {artist}"
                feature_texts.append(combined_features)
            
            self.feature_matrix = self.vectorizer.fit_transform(feature_texts)
            self.music_data = music_data
            logger.info(f"Built feature matrix with {len(music_data)} songs")
            return True
            
        except Exception as e:
            logger.error(f"Feature matrix building error: {e}")
            return False
    
    def calculate_similarities(self, user_preferences):
        """Calculate cosine similarities based on user preferences"""
        try:
            if self.feature_matrix is None or self.music_data is None:
                if not self.build_feature_matrix():
                    return []
            
            # Map music_id to indices
            music_id_to_index = {music['id']: idx for idx, music in enumerate(self.music_data)}
            preference_indices = [music_id_to_index.get(pref) for pref in user_preferences if pref in music_id_to_index]
            
            if not preference_indices:
                return []
            
            preference_vectors = self.feature_matrix[preference_indices]
            avg_preference = np.mean(preference_vectors.toarray(), axis=0)
            avg_preference = avg_preference.reshape(1, -1)
            
            similarities = cosine_similarity(avg_preference, self.feature_matrix)[0]
            
            recommendations = []
            music_similarities = list(enumerate(similarities))
            music_similarities.sort(key=lambda x: x[1], reverse=True)
            
            for idx, similarity in music_similarities:
                if idx not in preference_indices and similarity > 0.1:
                    music = self.music_data[idx].copy()
                    music['similarity_score'] = float(similarity)
                    recommendations.append(music)
                    if len(recommendations) >= 10:
                        break
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Similarity calculation error: {e}")
            return []
    
    def record_user_interaction(self, user_id, music_id, interaction_type='play'):
        """Record user interaction for improving recommendations"""
        try:
            connection = self.get_database_connection()
            cursor = connection.cursor()
            
            insert_pref = """
            INSERT INTO user_preferences (user_id, music_id, preference_score, interaction_type)
            VALUES (%s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE 
            preference_score = preference_score + VALUES(preference_score),
            created_at = CURRENT_TIMESTAMP
            """
            
            score = 1.0 if interaction_type == 'play' else 0.5
            cursor.execute(insert_pref, (user_id, music_id, score, interaction_type))
            
            update_popularity = """
            UPDATE music SET popularity_score = popularity_score + 0.1 WHERE id = %s
            """
            cursor.execute(update_popularity, (music_id,))
            
            connection.commit()
            
        except Error as e:
            logger.error(f"User interaction recording error: {e}")

# Initialize the recommendation system
music_system = MusicRecommendationSystem()
music_system.build_feature_matrix()

# def ensure_admin_account():
#     """Bootstrap admin account with secure password and Admin role"""
#     try:
#         connection = music_system.get_database_connection()
#         cursor = connection.cursor()
#         admin_name = 'admin'
#         admin_email = 'admin@gmail.com'
#         admin_password_hash = generate_password_hash('admin123')
#         admin_role = 'Admin'
#         # Insert if missing
#         cursor.execute(
#             "INSERT OR IGNORE INTO users (name, email, password, role) VALUES (?, ?, ?, ?)",
#             (admin_name, admin_email, admin_password_hash, admin_role)
#         )
#         # Ensure role/password are correct
#         cursor.execute(
#             "UPDATE users SET name = ?, password = ?, role = ? WHERE email = ?",
#             (admin_name, admin_password_hash, admin_role, admin_email)
#         )
#         connection.commit()
#         logger.info(f"Admin account ensured: username={admin_name}, email={admin_email}, role={admin_role}")
#     except Exception as e:
#         logger.error(f"Failed to ensure admin account: {e}")




@app.route('/api/music', methods=['GET'])
def get_music():
    """API endpoint to get music with optional filters"""
    try:
        query = request.args.get('query', '')
        genre = request.args.get('genre', '')
        year = request.args.get('year', '')
        
        music_list = music_system.get_all_music(query, genre, year)
        
        return jsonify({
            'success': True,
            'music': music_list,
            'count': len(music_list)
        })
        
    except Exception as e:
        logger.error(f"Get music API error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/recommend', methods=['POST'])
def get_recommendations():
    """API endpoint to get music recommendations based on user preferences"""
    try:
        data = request.get_json()
        preferences = data.get('preferences', [])
        user_id = data.get('user_id', 'anonymous')
        
        if not preferences:
            return jsonify({
                'success': False,
                'error': 'No preferences provided'
            }), 400
        
        recommendations = music_system.calculate_similarities(preferences)
        
        for pref in preferences:
            if isinstance(pref, int):
                music_system.record_user_interaction(user_id, pref, 'preference')
        
        return jsonify({
            'success': True,
            'recommendations': recommendations,
            'count': len(recommendations)
        })
        
    except Exception as e:
        logger.error(f"Recommendations API error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/play', methods=['POST'])
def record_play():
    """API endpoint to record music play events"""
    try:
        data = request.get_json()
        music_id = data.get('music_id')
        user_id = data.get('user_id', 'anonymous')
        duration = data.get('duration', 0)
        
        if not music_id:
            return jsonify({
                'success': False,
                'error': 'Music ID required'
            }), 400
        
        connection = music_system.get_database_connection()
        cursor = connection.cursor()
        
        insert_history = """
        INSERT INTO listening_history (user_id, music_id, play_duration)
        VALUES (%s, %s, %s)
        """
        cursor.execute(insert_history, (user_id, music_id, duration))
        
        music_system.record_user_interaction(user_id, music_id, 'play')
        
        connection.commit()
        
        return jsonify({
            'success': True,
            'message': 'Play event recorded'
        })
        
    except Exception as e:
        logger.error(f"Record play API error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """API endpoint to get system statistics"""
    try:
        connection = music_system.get_database_connection()
        cursor = connection.cursor(dictionary=True)
        
        cursor.execute("SELECT COUNT(*) as total_songs FROM music")
        total_songs = cursor.fetchone()['total_songs']
        
        cursor.execute("""
            SELECT genre, COUNT(*) as count 
            FROM music 
            GROUP BY genre 
            ORDER BY count DESC
        """)
        genre_stats = cursor.fetchall()
        
        cursor.execute("""
            SELECT title, artist, popularity_score 
            FROM music 
            ORDER BY popularity_score DESC 
            LIMIT 5
        """)
        popular_songs = cursor.fetchall()
        
        return jsonify({
            'success': True,
            'stats': {
                'total_songs': total_songs,
                'genres': genre_stats,
                'popular_songs': popular_songs
            }
        })
        
    except Exception as e:
        logger.error(f"Stats API error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    try:
        connection = music_system.get_database_connection()
        if connection and connection.is_connected():
            return jsonify({
                'success': True,
                'status': 'healthy',
                'database': 'connected'
            })
        else:
            return jsonify({
                'success': False,
                'status': 'unhealthy',
                'database': 'disconnected'
            }), 503
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return jsonify({
            'success': False,
            'status': 'error',
            'error': str(e)
        }), 500

@app.route('/search', methods=['POST'])
def search():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    query = request.form['search_query']
    results = music_system.get_all_music(query=query)
    
    return render_template('dashboard.html',
                         songs=results,
                         history=[],
                         name=session.get('user_name', 'User'),
                         music_list=bool(results))

@app.route('/dashboard')
@app.route('/dashboard/<int:song_id>')
def dashboard(song_id=None):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    try:
        user_id = session['user_id']
        name = session.get('user_name', 'User')
        connection = music_system.get_database_connection()
        cursor = connection.cursor(dictionary=True)

        current_song = None

        # 🎧 If user clicked a specific song
        if song_id:
            cursor.execute("SELECT * FROM music WHERE id = %s", (song_id,))
            current_song = cursor.fetchone()

            # 🕒 Record to recently played
            cursor.execute("""
                INSERT INTO listening_history (user_id, music_id, timestamp)
                VALUES (%s, %s, NOW())
            """, (user_id, song_id))
            connection.commit()

        # 🕒 Fetch recently played songs
        cursor.execute("""
            SELECT DISTINCT m.*
            FROM music m
            JOIN listening_history h ON m.id = h.music_id
            WHERE h.user_id = %s
            ORDER BY h.timestamp DESC
            LIMIT 10
        """, (user_id,))
        recently_played = cursor.fetchall()

        # 🎯 Recommend songs
        if song_id:
            # Recommend songs excluding current one
            cursor.execute("""
                SELECT * FROM music
                WHERE id != %s
                ORDER BY RAND()
                LIMIT 8
            """, (song_id,))
        else:
            # If no song selected, just random songs
            cursor.execute("""
                SELECT * FROM music
                ORDER BY RAND()
                LIMIT 8
            """)
        recommended_songs = cursor.fetchall()

        return render_template(
            'dashboard.html',
            name=name,
            current_song=current_song,
            history=recently_played,
            recommendations=recommended_songs
        )

    except Exception as e:
        logger.error(f"Error in dashboard: {e}")
        return render_template(
            'dashboard.html',
            name='User',
            message=str(e),
            current_song=None,
            history=[],
            recommendations=[]
        )
@app.route('/like_song/<int:song_id>', methods=['POST'])
def like_song(song_id):
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Not logged in'})

    user_id = session['user_id']
    try:
        connection = music_system.get_database_connection()
        cursor = connection.cursor()

        # Prevent duplicate likes
        cursor.execute("SELECT * FROM liked_songs WHERE user_id=%s AND music_id=%s", (user_id, song_id))
        if cursor.fetchone():
            return jsonify({'success': False, 'message': 'Already liked'})

        cursor.execute("INSERT INTO liked_songs (user_id, music_id) VALUES (%s, %s)", (user_id, song_id))
        connection.commit()
        return jsonify({'success': True})
    except Exception as e:
        logger.error(f"Error liking song: {e}")
        return jsonify({'success': False, 'message': str(e)})


@app.route('/add_to_playlist/<int:song_id>', methods=['POST'])
def add_to_playlist(song_id):
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Not logged in'})

    data = request.get_json()
    playlist_name = data.get('playlist_name')
    if not playlist_name:
        return jsonify({'success': False, 'message': 'Playlist name required'})

    user_id = session['user_id']
    try:
        connection = music_system.get_database_connection()
        cursor = connection.cursor()

        # Create playlist if not exists
        cursor.execute("""
            INSERT IGNORE INTO playlists (user_id, name)
            VALUES (%s, %s)
        """, (user_id, playlist_name))

        # Get playlist id
        cursor.execute("SELECT id FROM playlists WHERE user_id=%s AND name=%s", (user_id, playlist_name))
        playlist_id = cursor.fetchone()[0]

        # Add song to playlist
        cursor.execute("""
            INSERT INTO playlist_songs (playlist_id, music_id)
            VALUES (%s, %s)
        """, (playlist_id, song_id))
        connection.commit()

        return jsonify({'success': True})
    except Exception as e:
        logger.error(f"Error adding song to playlist: {e}")
        return jsonify({'success': False, 'message': str(e)})
    

    # ❤️ Favorites Page
@app.route('/favorites')
def favorites():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    try:
        user_id = session['user_id']
        connection = music_system.get_database_connection()
        cursor = connection.cursor(dictionary=True)

        # Fetch liked songs for this user
        cursor.execute("""
            SELECT m.*
            FROM liked_songs l
            JOIN music m ON l.music_id = m.id
            WHERE l.user_id = %s
        """, (user_id,))
        liked_songs = cursor.fetchall()

        return render_template('favorites.html', songs=liked_songs)

    except Exception as e:
        logger.error(f"Error loading favorites: {e}")
        return render_template('favorites.html', songs=[], message=str(e))


# 🎧 Playlists Page
@app.route('/playlists')
def playlists():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    try:
        user_id = session['user_id']
        connection = music_system.get_database_connection()
        cursor = connection.cursor(dictionary=True)

        # Fetch playlists created by the logged-in user
        cursor.execute("SELECT * FROM playlists WHERE user_id = %s", (user_id,))
        playlists = cursor.fetchall()

        cursor.close()
        connection.close()

        return render_template('playlists.html', playlists=playlists)

    except Exception as e:
        print(f"Error loading playlists: {e}")
        return render_template('playlists.html', playlists=[], message=str(e))



# 🎵 View songs in a specific playlist
@app.route('/playlist/<int:playlist_id>')
def playlist_detail(playlist_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    try:
        connection = music_system.get_database_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute("""
            SELECT m.*
            FROM playlist_songs ps
            JOIN music m ON ps.music_id = m.id
            WHERE ps.playlist_id = %s
        """, (playlist_id,))
        songs = cursor.fetchall()

        cursor.execute("SELECT name FROM playlists WHERE id = %s", (playlist_id,))
        playlist = cursor.fetchone()

        return render_template('playlist_detail.html',
                               playlist_name=playlist['name'] if playlist else "My Playlist",
                               songs=songs)

    except Exception as e:
        logger.error(f"Error loading playlist songs: {e}")
        return render_template('playlist_detail.html', songs=[], message=str(e))



@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        fullname = request.form['fullname']
        email = request.form['email']
        password = request.form['password']

        hashed_password = generate_password_hash(password)

        try:
            connection = music_system.get_database_connection()
            cursor = connection.cursor()

            # Check if user already exists
            cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
            existing_user = cursor.fetchone()
            if existing_user:
                cursor.close()
                connection.close()
                return render_template('signup.html', error="⚠️ Email already exists. Try logging in.")

            # Insert new user
            cursor.execute(
                "INSERT INTO users (name, email, password) VALUES (%s, %s, %s)",
                (fullname, email, hashed_password)
            )
            connection.commit()

            cursor.close()
            connection.close()

            # Flash success message
            flash("✅ Your account has been created successfully. Please log in.")
            return redirect(url_for('login'))  # redirect to login page

        except Error as e:
            logger.error(f"Signup error: {e}")
            return render_template('signup.html', error="Something went wrong. Please try again.")

    return render_template('signup.html')



@app.route('/preferences', methods=['GET', 'POST'])
def preferences():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']

    if request.method == 'POST':
        selected_genres = request.form.getlist('genres')

        connection = music_system.get_database_connection()
        cursor = connection.cursor(dictionary=True)

        genre_placeholders = ','.join(['%s'] * len(selected_genres))
        cursor.execute(f"SELECT id FROM music WHERE genre IN ({genre_placeholders})", selected_genres)
        songs = cursor.fetchall()

        for song in songs:
            music_system.record_user_interaction(user_id, song['id'], 'preference')

        return redirect(url_for('dashboard'))

    connection = music_system.get_database_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT DISTINCT genre FROM music")
    genres = [row[0] for row in cursor.fetchall()]
    
    return render_template('preferences.html', genres=genres)

from werkzeug.security import check_password_hash

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # ✅ Use music_system to get a database connection
        connection = music_system.get_database_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()

        cursor.close()
        connection.close()

        if user and check_password_hash(user['password'], password):
            # ✅ Store session details
            session['user_id'] = user['id']
            session['user_name'] = user['name']
            session['user_email'] = user['email']

            flash("✅ Login successful!", "success")
            return redirect(url_for('home'))
        else:
            flash("❌ Invalid email or password", "error")
            return redirect(url_for('login'))

    return render_template('login.html')


@app.route('/home')
def home():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    songs = music_system.get_all_music()
    return render_template('home.html', songs=songs)




@app.route('/update_recommendation/<int:song_id>', methods=['POST'])
def update_recommendation(song_id):
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'Unauthorized'}), 401

    try:
        user_id = session['user_id']
        connection = music_system.get_database_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute("""
            INSERT INTO listening_history (user_id, music_id, timestamp)
            VALUES (%s, %s, %s)
        """, (user_id, song_id, datetime.now()))
        connection.commit()

        music_system.record_user_interaction(user_id, song_id, 'play')

        cursor.execute("""
            SELECT DISTINCT m.*
            FROM music m
            JOIN listening_history h ON m.id = h.music_id
            WHERE h.user_id = %s
            ORDER BY h.timestamp DESC
            LIMIT 10
        """, (user_id,))
        recently_played = cursor.fetchall()

        cursor.execute("""
            SELECT music_id
            FROM user_preferences
            WHERE user_id = %s
        """, (user_id,))
        preferences = [row['music_id'] for row in cursor.fetchall()]

        recommendations = music_system.calculate_similarities(preferences)

        cursor.close()

        return jsonify({
            'success': True,
            'recently_played': recently_played,
            'recommendations': recommendations
        }), 200

    except Exception as e:
        logger.error(f"Update recommendation error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
    

@app.route('/admin/songs')
def admin_songs():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    try:
        songs = music_system.get_all_music()
        total_songs = len(songs)
        genres = list(set(s.get('genre') for s in songs if s.get('genre')))
        return render_template(
            'admin_songs.html',
            songs=songs,
            total_songs=total_songs,
            genre_count=len(genres)
        )
    except Exception as e:
        logger.error(f"Admin error: {e}")
        return render_template('admin_songs.html', songs=[], total_songs=0, genre_count=0, message=str(e))



@app.route('/listen/<int:song_id>', methods=['POST'])
def listen(song_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    try:
        user_id = session['user_id']
        connection = music_system.get_database_connection()
        cursor = connection.cursor()

        cursor.execute(
            "INSERT INTO listening_history (user_id, music_id) VALUES (%s, %s)",
            (user_id, song_id)
        )
        connection.commit()

        return jsonify({'message': 'Recorded'})
    except Exception as e:
        logger.error(f"Listen error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/')
def landing():
    return render_template('landing.html')

@app.route('/test')
def test_get_music():
    songs = music_system.get_all_music()
    logger.info(f"Test route - songs fetched: {len(songs)}")
    return jsonify(songs)

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'error': 'Endpoint not found'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'success': False,
        'error': 'Internal server error'
    }), 500

if __name__ == '__main__':
    logger.info("Starting Music Recommendation System API...")
    logger.info("Make sure MySQL is running and database is configured properly.")
    logger.info("API will be available at: http://localhost:5000")
    music_system.insert_sample_data()  # Ensure sample data is inserted
    # ensure_admin_account()  # Ensure admin exists
    # logger.info(" Admin account ready: email=admin@gmail.com, password=admin123, role=Admin")
    app.run(debug=True, host='0.0.0.0', port=5000)
