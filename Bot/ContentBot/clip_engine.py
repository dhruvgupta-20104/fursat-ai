import random
from moviepy.editor import VideoFileClip

from Bot.ContentBot.viral_detector import ViralMomentDetector
from Bot.ContentBot.config import Config

class ClipGenerator:
    def __init__(self, video_path):
        self.clip = VideoFileClip(video_path)
        self.duration = self.clip.duration

    def _find_viral_moments(self):
        """Identify best moments using audio analysis"""
        audio_path = "temp_audio.wav"
        self.clip.audio.write_audiofile(audio_path)
        detector = ViralMomentDetector(audio_path)
        return detector.find_peaks()

    def generate_clips(self):
        clips = []
        viral_moments = self._find_viral_moments()

        # Generate viral-focused clips
        for peak in viral_moments[:4]:  # Top 4 peaks
            start = max(0, peak - 5)  # 5s before peak
            end = min(self.duration, peak + 5)  # 5s after peak
            clips.append(self.clip.subclip(start, end))

        # Fill remaining slots with random clips
        remaining = Config.CLIPS_PER_VIDEO - len(clips)
        for _ in range(remaining):
            if random.random() < 0.8:  # 80% short clips
                clip_range = Config.SHORT_CLIP_RANGE
            else:
                clip_range = Config.LONG_CLIP_RANGE

            start = random.uniform(0, self.duration - clip_range[1])
            end = start + random.uniform(*clip_range)
            clips.append(self.clip.subclip(start, end))

        return clips