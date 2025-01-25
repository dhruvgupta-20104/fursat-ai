from pytube import YouTube, Channel
import os

from Bot.ContentBot.config import Config as config

def fetch_top_videos(channel_url: str) -> list:
    """Fetch top viewed videos from a YouTube channel"""
    channel = Channel(channel_url)
    return sorted(
        [v for v in channel.videos if v.views >= config.VIEW_THRESHOLD],
        key=lambda x: x.views,
        reverse=True
    )[:config.MAX_VIDEOS]

def download_video(video_url: str, output_dir: str = "raw_videos") -> str:
    """Download YouTube video and return local path"""
    yt = YouTube(video_url)
    stream = yt.streams.filter(
        progressive=True,
        file_extension='mp4'
    ).order_by('resolution').desc().first()

    os.makedirs(output_dir, exist_ok=True)
    return stream.download(output_dir)
