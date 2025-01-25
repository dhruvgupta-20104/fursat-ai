import librosa
import numpy as np

class ViralMomentDetector:
    def __init__(self, audio_path):
        self.y, self.sr = librosa.load(audio_path)

    def find_peaks(self, window_size=5):
        """Identify high-energy moments using RMS"""
        rms = librosa.feature.rms(y=self.y, frame_length=2048)[0]
        smoothed = np.convolve(rms, np.ones(window_size)/window_size, mode='same')
        peaks = np.where(smoothed > Config.PEAK_THRESHOLD)[0]
        return [(p/len(rms)*len(self.y)/self.sr) for p in peaks]