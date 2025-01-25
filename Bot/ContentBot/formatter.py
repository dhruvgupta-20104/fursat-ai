from moviepy.video.fx.all import crop, resize

def format_for_reels(clip):
    """Convert to 9:16 vertical format"""
    w, h = clip.size

    # Calculate target dimensions
    target_width = h * 9 // 16
    target_height = h

    if w < target_width:
        # Horizontal padding needed
        clip = resize(clip, width=target_width)
    else:
        # Horizontal cropping
        x_center = w / 2
        clip = crop(clip,
                  x_center=x_center,
                  width=target_width,
                  height=target_height)

    # Final resize for consistency
    return resize(clip, height=1080)
