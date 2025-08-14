from moviepy import VideoFileClip, concatenate_videoclips, CompositeVideoClip, vfx

# Load the two video clips
clip1 = VideoFileClip("matched_second_video.mp4")
clip2 = VideoFileClip("hp_sheet.mp4")

clips = [
	clip2.with_end(2),
	clip1.with_start(1).with_effects([vfx.CrossFadeIn(1)])
	]

# Concatenate them into one clip
#combined = concatenate_videoclips([clip2, clip1])
	
final_clip = CompositeVideoClip(clips)
final_clip.write_videofile("final_clip.mp4")

# Write the result to a new file
#combined.write_videofile("joined_video.mp4")