import os
import time
import random
import obspython as obs

# Primary directory for new videos
videos_directory = "/home/ratio/www/video"
# Directory for random videos during idle times
idle_videos_directory = "/home/ratio/www/newvideos"
source_name = "ass"

last_played_video = ""
last_idle_video = ""
last_check = 0
idle_video_list = []  # List to manage idle videos playback

def play_video(video_path):
    global last_played_video
    source = obs.obs_get_source_by_name(source_name)
    if source:
        settings = obs.obs_data_create()
        obs.obs_data_set_string(settings, "local_file", video_path)
        obs.obs_source_update(source, settings)
        obs.obs_data_release(settings)
        obs.obs_source_release(source)
        last_played_video = video_path
        print(f"Now playing: {video_path}")

def get_latest_video(directory):
    try:
        files = [f for f in os.listdir(directory) if f.endswith(".mp4")]
        if not files:
            return None
        files.sort(key=lambda x: os.path.getmtime(os.path.join(directory, x)), reverse=True)
        return os.path.join(directory, files[0])
    except Exception as e:
        print(f"Error getting latest video: {e}")
        return None

def play_random_idle_video():
    global idle_video_list, last_idle_video
    try:
        if not idle_video_list:
            idle_video_list = [os.path.join(idle_videos_directory, f) for f in os.listdir(idle_videos_directory) if f.endswith(".mp4")]
            random.shuffle(idle_video_list)  # Shuffle to ensure random playback
        
        while idle_video_list:
            video_path = idle_video_list.pop()
            if video_path != last_idle_video or len(idle_video_list) == 0:  # Avoid immediate repetition unless it's the only video
                play_video(video_path)
                last_idle_video = video_path
                return
    except Exception as e:
        print(f"Error playing random idle video: {e}")

def script_tick(seconds):
    global last_check
    current_time = time.time()
    # Check for a new video every 10 seconds
    if current_time - last_check > 10:
        latest_video = get_latest_video(videos_directory)
        if latest_video and latest_video != last_played_video:
            play_video(latest_video)
        elif not latest_video or latest_video == last_played_video:  # No new video found or waiting for new ones
            play_random_idle_video()
        last_check = current_time

def script_description():
    return "Automatically plays new videos added to a specified folder or random videos from another folder when idle."

def script_properties():
    props = obs.obs_properties_create()
    obs.obs_properties_add_path(props, "videos_directory", "Videos Directory", obs.OBS_PATH_DIRECTORY, None, videos_directory)
    obs.obs_properties_add_path(props, "idle_videos_directory", "Idle Videos Directory", obs.OBS_PATH_DIRECTORY, None, idle_videos_directory)
    obs.obs_properties_add_text(props, "source_name", "Media Source Name", obs.OBS_TEXT_DEFAULT)
    return props

def script_update(settings):
    global videos_directory, idle_videos_directory, source_name
    videos_directory = obs.obs_data_get_string(settings, "videos_directory")
    idle_videos_directory = obs.obs_data_get_string(settings, "idle_videos_directory")
    source_name = obs.obs_data_get_string(settings, "source_name")
