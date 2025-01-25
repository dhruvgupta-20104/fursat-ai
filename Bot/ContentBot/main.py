import os

from yt_processor import fetch_top_videos, download_video
from clip_engine import generate_clips
from caption_engine import add_captions
from formatter import format_for_reels
from ig_uploader import InstagramManager

def process_channel(channel_url: str):
    """Full processing pipeline"""
    # Setup directories
    os.makedirs("raw_videos", exist_ok=True)
    os.makedirs("processed", exist_ok=True)
    os.makedirs("output", exist_ok=True)

    # Fetch and process videos
    videos = fetch_top_videos(channel_url)
    ig = InstagramManager()

    for vid in videos:
        try:
            # Download source video
            local_path = download_video(vid.watch_url)

            # Generate clips
            clips = generate_clips(local_path)

            # Process each clip
            for idx, clip in enumerate(clips):
                processed = format_for_reels(add_captions(clip))
                output_path = f"output/reel_{vid.video_id}_{idx}.mp4"
                processed.write_videofile(
                    output_path,
                    codec="libx264",
                    audio_codec="aac",
                    threads=4,
                    logger=None
                )

                # Upload to Instagram
                ig.upload_reel(output_path, f"Live performance @{channel_url.split('/')[-1]}")

        except Exception as e:
            print(f"Failed processing {vid.title}: {str(e)}")
