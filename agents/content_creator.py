# agents/content_creator.py

import os
from typing import Dict, Any
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip, AudioFileClip
import openai
from pytube import YouTube
import logging

from core.agent_base import BaseAgent

class ContentCreatorAgent(BaseAgent):
    def __init__(self):
        super().__init__("ContentCreator")
        self.logger = logging.getLogger("ContentCreatorAgent")
        self.openai_client = openai.Client(api_key=os.getenv("OPENAI_API_KEY"))
        
    async def process_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        try:
            content_type = message.get("content_type")
            content_url = message.get("content_url")

            if content_type == "youtube":
                # Download and process YouTube video
                video_data = await self._process_youtube_video(content_url)

                # Generate content using GPT
                caption = await self._generate_caption(video_data["title"])

                # Create short video
                short_path = await self._create_short(
                    video_data["path"],
                    caption,
                    video_data["title"]
                )

                # Schedule content
                schedule_result = await self._schedule_content(short_path, caption)

                return {
                    "status": "success",
                    # "video_path": short_path,
                    # "caption": caption,
                    # "schedule": schedule_result
                }

            return {"error": "Unsupported content type"}

        except Exception as e:
            self.logger.error(f"Error processing content: {str(e)}")
            return {"error": str(e)}

    async def _process_youtube_video(self, url: str) -> Dict[str, str]:
        """Download and process YouTube video."""
        try:
            yt = YouTube(url)
            video = yt.streams.filter(progressive=True, file_extension='mp4').first()
            output_path = f"downloads/{yt.video_id}.mp4"
            video.download(filename=output_path)

            return {
                "title": yt.title,
                "path": output_path,
                "duration": yt.length
            }
        except Exception as e:
            self.logger.error(f"Error downloading video: {str(e)}")
            raise

    async def _generate_caption(self, title: str) -> str:
        """Generate engaging caption using GPT."""
        try:
            response = await self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a social media expert creating engaging captions."},
                    {"role": "user", "content": f"Create a short, engaging caption for a video titled: {title}"}
                ]
            )
            return response.choices[0].message.content
        except Exception as e:
            self.logger.error(f"Error generating caption: {str(e)}")
            raise

    async def _create_short(self, video_path: str, caption: str, title: str) -> str:
        """Create a short video with caption overlay."""
        try:
            clip = VideoFileClip(video_path).subclip(0, 60)
            text_clip = TextClip(
                caption,
                fontsize=24,
                color='white',
                bg_color='black',
                font='Arial-Bold'
            ).set_position('bottom').set_duration(clip.duration)

            final_clip = CompositeVideoClip([clip, text_clip])
            output_path = f"generated/short_{title}.mp4"
            final_clip.write_videofile(output_path)

            return output_path
        except Exception as e:
            self.logger.error(f"Error creating short: {str(e)}")
            raise

    async def _schedule_content(self, video_path: str, caption: str) -> Dict[str, Any]:
        """Schedule content for posting."""
        # Implementation for scheduling content
        # This would integrate with your preferred scheduling platform
        return {
            "scheduled": True,
            "platform": "livegig.me",
            "timestamp": "2024-01-23T10:00:00Z"
        }

