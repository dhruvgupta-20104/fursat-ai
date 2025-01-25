import os
import json

class Config:
    # YouTube Configuration
    YT_CHANNELS = ["@LiveGigMeOfficial"]  # Example channel
    MAX_VIDEOS = 5  # Reduced for testing
    VIEW_THRESHOLD = 50000  # Minimum views to process

    # Reel Configuration
    CLIPS_PER_VIDEO = 12
    SHORT_CLIP_RANGE = (15, 30)  # Seconds
    LONG_CLIP_RANGE = (45, 60)   # Seconds
    ASPECT_RATIO = (9, 16)       # Instagram Reels format

    # Instagram Credentials (Store in .env)
    IG_USERNAME = os.getenv("IG_USERNAME")
    IG_PASSWORD = os.getenv("IG_PASSWORD")
    
    # Video Selection Criteria
    MIN_VIEWS = 5000
    MIN_ENGAGEMENT_RATE = 0.05  # (likes + comments)/views
    TARGET_GENRES = ["rock", "jazz", "classical"]

    # Caption Styling
    FONT = "Arial-Bold"
    FONT_SIZE_RATIO = 0.075  # 7.5% of video height
    TEXT_COLOR = "#FFFFFF"
    STROKE_COLOR = "#000000"

    # Instagram Scheduling
    MAX_DAILY_POSTS = 2
    PRIME_TIMES = [9, 12, 18]  # Local time hours

    # Audio Analysis
    PEAK_THRESHOLD = 0.8  # For viral moment detection

    @classmethod
    def ffmpeg_path(cls):
        try:
            with open('config.json') as f:
                return json.load(f).get('ffmpeg_path', 'ffmpeg')
        except FileNotFoundError:
            return 'ffmpeg'

# Update MoviePy config
os.environ["IMAGEIO_FFMPEG_EXE"] = Config.ffmpeg_path()