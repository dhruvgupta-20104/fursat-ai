from instabot import Bot
import time
import logging
import os
import random

from Bot.ContentBot.config import Config

class InstagramManager:
    MAX_RETRIES = 3

    def __init__(self):
        self.bot = Bot()
        self.bot.login(
            username=os.getenv("IG_USERNAME"),
            password=os.getenv("IG_PASSWORD"),
            proxy=None
        )
        self.post_count = 0
        self.last_post_time = None

    def _schedule_check(self):
        """Enforce posting limits"""
        if self.post_count >= Config.MAX_DAILY_POSTS:
            raise Exception("Daily post limit reached")

        if self.last_post_time and (time.time() - self.last_post_time < 3600):
            time.sleep(3600 - (time.time() - self.last_post_time))

    def upload_reel(self, path, caption):
        for attempt in range(self.MAX_RETRIES):
            try:
                self._schedule_check()
                result = self.bot.upload_video(
                    path,
                    caption=self._format_caption(caption),
                    thumbnail=None
                )
                self.post_count += 1
                self.last_post_time = time.time()
                return result
            except Exception as e:
                logging.error(f"Upload failed (attempt {attempt+1}): {str(e)}")
                time.sleep(60 ** (attempt + 1))

        logging.critical(f"Permanent failure uploading {path}")
        return False

    def _format_caption(self, text):
        return f"{text}\\n\\n🎵 #LiveGigMe #LiveMusic #{random.choice(Config.TARGET_GENRES)}"
