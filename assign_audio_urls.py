import mysql.connector
import random

# 🟣 Sample free audio previews (can be reused across songs)
sample_audio_urls = [
    "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3",
    "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-2.mp3",
    "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-3.mp3",
    "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-4.mp3",
    "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-5.mp3",
    "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-6.mp3",
    "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-7.mp3"
]

# 🔌 Connect to your MySQL database
# Uses environment variables if set, otherwise defaults to Docker MySQL values
import os
db = mysql.connector.connect(
    host=os.getenv('MYSQL_HOST', 'localhost'),
    user=os.getenv('MYSQL_USER', 'root'),
    password=os.getenv('MYSQL_PASSWORD', 'rootpassword'),  # Docker MySQL password
    database=os.getenv('MYSQL_DATABASE', 'music_recommendation_db')
)

cursor = db.cursor()

# 🔍 Get all songs with missing audio_url
cursor.execute("SELECT id FROM music WHERE audio_url IS NULL OR audio_url = ''")
songs_missing_audio = cursor.fetchall()

print(f"Found {len(songs_missing_audio)} songs missing audio_url...")

# 🔁 Assign a random sample audio to each
for (song_id,) in songs_missing_audio:
    url = random.choice(sample_audio_urls)
    cursor.execute("UPDATE music SET audio_url = %s WHERE id = %s", (url, song_id))

# ✅ Save changes
db.commit()
cursor.close()
db.close()

print("Done: Sample audio assigned to all missing songs.")
