import whisper
from moviepy.editor import TextClip, CompositeVideoClip

model = whisper.load_model("base")

def add_captions(clip):
    """Add auto-generated captions to clip"""
    # Extract audio
    audio_path = "temp_audio.wav"
    clip.audio.write_audiofile(audio_path)

    # Transcribe with timing
    result = model.transcribe(audio_path, word_timestamps=True)

    # Create text clips
    text_clips = []
    for segment in result["segments"]:
        txt = segment["text"].upper()
        txt_clip = TextClip(txt, fontsize=24, color='white',
                           font='Arial-Bold', stroke_color='black',
                           stroke_width=1).set_position(('center', 0.85),
                           relative=True).set_duration(segment["end"] - segment["start"]).set_start(segment["start"])
        text_clips.append(txt_clip)

    return CompositeVideoClip([clip] + text_clips)
